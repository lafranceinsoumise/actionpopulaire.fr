import hashlib
import json
import random
import re
from datetime import timedelta
from secrets import token_urlsafe
from urllib.parse import urljoin

import ics
import pytz
from django import forms
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVector, SearchRank
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import Case, Sum, Count, When, CharField, F, Q, OuterRef, Subquery
from django.db.models import JSONField, Prefetch
from django.db.models.functions import Coalesce
from django.template.defaultfilters import floatformat
from django.utils import formats, timezone
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from dynamic_filenames import FilePattern
from ics import Organizer
from slugify import slugify
from stdimage.models import StdImageField

from agir.carte.models import StaticMapImage
from agir.gestion.typologies import TypeProjet, TypeDocument
from agir.groups.models import Membership, SupportGroup
from agir.lib import html
from agir.lib.form_fields import CustomJSONEncoder, DateTimePickerWidget
from agir.lib.html import textify, sanitize_html
from agir.lib.model_fields import FacebookEventField
from agir.lib.models import (
    BaseAPIResource,
    AbstractLabel,
    ContactMixin,
    LocationMixin,
    ImageMixin,
    DescriptionMixin,
    DescriptionField,
    BaseSubtype,
    TimeStampedModel,
    banner_image_file_path,
)
from agir.lib.search import PrefixSearchQuery
from agir.lib.utils import front_url, resize_and_autorotate, is_absolute_url

__all__ = [
    "Event",
    "EventTag",
    "EventSubtype",
    "RSVP",
    "Calendar",
    "OrganizerConfig",
    "EventImage",
    "IdentifiedGuest",
    "JitsiMeeting",
    "GroupAttendee",
]


class EventQuerySet(models.QuerySet):
    def public(self):
        return self.filter(visibility=Event.VISIBILITY_PUBLIC)

    def listed(self):
        return self.public().filter(do_not_list=False)

    def is_2022(self):
        return self.filter(for_users=Event.FOR_USERS_2022)

    def upcoming(self, as_of=None, published_only=True):
        if as_of is None:
            as_of = timezone.now()

        condition = models.Q(end_time__gte=as_of)
        if published_only:
            condition &= models.Q(visibility=Event.VISIBILITY_PUBLIC)

        return self.filter(condition)

    def past(self, as_of=None, published_only=True):
        if as_of is None:
            as_of = timezone.now()

        condition = models.Q(end_time__lt=as_of)
        if published_only:
            condition &= models.Q(visibility=Event.VISIBILITY_PUBLIC)
        return self.filter(condition)

    def acceptable_for_group_certification(self, limit_days=62, time_ref=None):
        if time_ref is None:
            time_ref = timezone.now()

        return (
            self.public()
            .filter(subtype__is_acceptable_for_group_certification=True)
            .filter(
                start_time__range=(
                    time_ref - timedelta(days=limit_days),
                    time_ref,
                )
            )
        )

    def with_person_organizer_configs(self, person):
        return self.prefetch_related(
            Prefetch(
                "organizer_configs",
                queryset=OrganizerConfig.objects.filter(
                    Q(person=person)
                    | Q(
                        as_group_id__in=Membership.objects.filter(
                            person=person,
                            membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
                        ).values_list("supportgroup_id", flat=True)
                    )
                ).distinct("pk"),
                to_attr="_pf_person_organizer_configs",
            )
        )

    def with_organizer_groups(self):
        return self.prefetch_related(
            Prefetch(
                "organizers_groups",
                to_attr="_pf_organizer_groups",
            )
        )

    def with_group_attendees(self):
        return self.prefetch_related(
            Prefetch(
                "organizers_groups",
                to_attr="_pf_group_attendees",
            )
        )

    def with_person_rsvps(self, person):
        return self.prefetch_related(
            Prefetch(
                "rsvps",
                queryset=RSVP.objects.filter(person=person),
                to_attr="_pf_person_rsvps",
            )
        )

    def with_static_map_image(self):
        return self.annotate(
            static_map_image=Subquery(
                StaticMapImage.objects.filter(
                    center__dwithin=(
                        OuterRef("coordinates"),
                        StaticMapImage.UNIQUE_CENTER_MAX_DISTANCE,
                    ),
                ).values("image")[:1],
            )
        )

    def with_event_card_serializer_prefetch(self):
        return (
            self.select_related("subtype")
            .prefetch_related("organizer_configs")
            .with_organizer_groups()
            .with_group_attendees()
            .with_static_map_image()
        )

    def with_serializer_prefetch(self, person):
        qs = (
            self.select_related("subtype", "volunteer_application_form")
            .prefetch_related(
                "organizer_configs", "event_speakers", "event_speakers__person"
            )
            .with_organizer_groups()
            .with_group_attendees()
            .with_static_map_image()
        )
        if person:
            qs = qs.with_person_rsvps(person).with_person_organizer_configs(person)
        return qs

    def with_participants(self):
        confirmed_guests = Q(rsvps__identified_guests__status=RSVP.STATUS_CONFIRMED)
        confirmed_rsvps = Q(rsvps__status=RSVP.STATUS_CONFIRMED)
        canceled_guests = Q(rsvps__identified_guests__status=RSVP.STATUS_CANCELED)
        canceled_rsvps = Q(rsvps__status=RSVP.STATUS_CANCELED)

        return self.annotate(
            all_attendee_count=Case(
                When(
                    subscription_form=None,
                    then=Coalesce(
                        Sum("rsvps__guests", filter=~canceled_rsvps)
                        + Count("rsvps", filter=~canceled_rsvps),
                        0,
                    ),
                ),
                default=Coalesce(
                    Count("rsvps__identified_guests", filter=~canceled_guests)
                    + Count("rsvps", filter=~canceled_rsvps),
                    0,
                ),
                output_field=CharField(),
            ),
            confirmed_attendee_count=Case(
                When(payment_parameters=None, then=F("all_attendee_count")),
                When(
                    subscription_form=None,
                    then=Coalesce(
                        Sum("rsvps__guests", filter=confirmed_rsvps)
                        + Count("rsvps", filter=confirmed_rsvps),
                        0,
                    ),
                ),
                default=Coalesce(
                    Count("rsvps__identified_guests", filter=confirmed_guests)
                    + Count("rsvps", filter=confirmed_rsvps),
                    0,
                ),
                output_field=CharField(),
            ),
        )

    def search(self, query):
        """Recherche sur l'ensemble des champs texte de l'événement"""
        vector = (
            SearchVector(models.F("name"), config="french_unaccented", weight="A")
            + SearchVector(
                models.F("location_name"), config="french_unaccented", weight="B"
            )
            + SearchVector(
                models.F("location_city"), config="french_unaccented", weight="B"
            )
            + SearchVector(
                models.F("location_zip"), config="french_unaccented", weight="B"
            )
            + SearchVector(
                models.F("description"), config="french_unaccented", weight="C"
            )
            + SearchVector(
                models.F("report_content"), config="french_unaccented", weight="C"
            )
        )
        query = PrefixSearchQuery(query, config="french_unaccented")

        return (
            self.annotate(search=vector)
            .filter(search=query)
            .annotate(rank=SearchRank(vector, query))
            .order_by("-rank")
        )

    def near(self, coordinates=None, radius=None):
        if not coordinates:
            return self

        if radius is None:
            from agir.people.models import Person

            radius = Person.DEFAULT_ACTION_RADIUS

        return (
            self.exclude(coordinates__isnull=True)
            .filter(coordinates__dwithin=(coordinates, D(km=radius)))
            .annotate(distance=Distance("coordinates", coordinates))
        )

    def simple_search(self, query):
        """Cherche uniquement sur le nom de l'événement, le nom du lieu et le nom de la ville"""
        vector = (
            SearchVector(models.F("name"), config="french_unaccented", weight="A")
            + SearchVector(
                models.F("location_name"), config="french_unaccented", weight="B"
            )
            + SearchVector(
                models.F("location_city"), config="french_unaccented", weight="C"
            )
        )

        query = PrefixSearchQuery(query, config="french_unaccented")

        return (
            self.annotate(search=vector)
            .filter(search=query)
            .annotate(rank=SearchRank(vector, query))
            .order_by("-rank")
        )

    def national(self):
        return self.filter(calendars__slug="national")

    def grand(self):
        return self.filter(calendars__slug="grands-evenements")

    def for_segment_subscriber(self, person):
        from agir.mailing.models import Segment

        segmented_events = self.exclude(suggestion_segment_id__isnull=True)
        segments = Segment.objects.filter(
            pk__in=segmented_events.values_list("suggestion_segment_id", flat=True)
        ).distinct("pk")
        return segmented_events.filter(
            suggestion_segment_id__in=[
                segment.id for segment in segments if segment.is_subscriber(person)
            ]
        )


class RSVPQuerySet(models.QuerySet):
    def upcoming(self, as_of=None, published_only=True):
        if as_of is None:
            as_of = timezone.now()

        condition = models.Q(event__end_time__gte=as_of)
        if published_only:
            condition &= models.Q(event__visibility=Event.VISIBILITY_PUBLIC)

        return self.filter(condition)

    def past(self, as_of=None, published_only=True):
        if as_of is None:
            as_of = timezone.now()

        condition = models.Q(event__end_time__lt=as_of)
        if published_only:
            condition &= models.Q(event__visibility=Event.VISIBILITY_PUBLIC)

        return self.filter(condition)


class CustomDateTimeFormField(forms.DateTimeField):
    widget = DateTimePickerWidget

    def prepare_value(self, value):
        return value


class CustomDateTimeField(models.DateTimeField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": CustomDateTimeFormField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


def get_default_subtype():
    subtype = (
        EventSubtype.objects.filter(type=EventSubtype.TYPE_PUBLIC_ACTION)
        .order_by("created")
        .values("id")
        .first()
    )

    return subtype and subtype["id"]


report_image_path = FilePattern(
    filename_pattern="{app_label}/{model_name}/{instance.id}/report_banner{ext}"
)


class EventManager(models.Manager.from_queryset(EventQuerySet)):
    def create(self, *args, **kwargs):
        subtype = kwargs.get("subtype", None)
        if subtype:
            kwargs["description"] = kwargs.get(
                "description", subtype.default_description
            )
            kwargs["image"] = kwargs.get("image", subtype.default_image)
        return self.create_event(*args, **kwargs)

    def create_event(
        self,
        organizer_person=None,
        organizer_group=None,
        event_speakers=None,
        **kwargs,
    ):
        with transaction.atomic():
            event = self.model(**kwargs)
            event.save(using=self._db)

            if organizer_person is not None:
                OrganizerConfig.objects.create(
                    event=event,
                    person=organizer_person,
                    as_group=organizer_group,
                )
                RSVP.objects.create(event=event, person=organizer_person)

            event_speakers = event_speakers or []

            if event_speakers:
                event.event_speakers.add(*event_speakers)
                RSVP.objects.bulk_create(
                    [
                        RSVP(person_id=es.person_id, event=event)
                        for es in event_speakers
                    ],
                    ignore_conflicts=True,
                )

            return event


EVENT_PAYMENT_PARAMETERS_DOCUMENTATION = mark_safe(
    """
<p>Doit être un objet JSON qui peut contenir les clés suivantes :</p>
<ul>
<li><strong>pricing</strong> : un prix fixe en centimes</li>
<li><strong>free_pricing</strong> : l'id d'un champ numérique du formulaire associé à l'événement qui sera utilisé 
comme prix pour l'événement</li>
<li><strong>mappings</strong> : Une liste de mappings entre réponses au formulaire et prix correspondant. Chaque 
mapping est un objet JSON avec un champ <em>fields</em> qui liste les champs à utiliser, et le champ <em>mapping</em>
lui-même.</li>
<li><strong>payment_modes</strong> : indique la liste des modes de paiement admissibles pour cet événement.</li>
<li><strong>admin_payment_modes</strong> : Idem, mais à utiliser pour les modes de paiement côté admin.</li>
<li><strong>allow_checks_upto</strong> : arrête d'accepter les chèques N jours avant l'événement (7 par défaut).</li>
</ul>
"""
)


class Event(
    ExportModelOperationsMixin("event"),
    BaseAPIResource,
    LocationMixin,
    ImageMixin,
    DescriptionMixin,
    ContactMixin,
):
    """
    Model that represents an event
    """

    objects = EventManager()

    name = models.CharField(
        _("nom"), max_length=255, blank=False, help_text=_("Le nom de l'événement")
    )

    VISIBILITY_ADMIN = "A"
    VISIBILITY_ORGANIZER = "O"
    VISIBILITY_PUBLIC = "P"
    VISIBILITY_CHOICES = (
        (VISIBILITY_ADMIN, "Caché"),
        (VISIBILITY_ORGANIZER, "Visible par les organisateurs"),
        (VISIBILITY_PUBLIC, "Public"),
    )

    visibility = models.CharField(
        "Visibilité",
        max_length=1,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
    )

    subtype = models.ForeignKey(
        "EventSubtype",
        verbose_name="Sous-type",
        related_name="events",
        on_delete=models.PROTECT,
        default=get_default_subtype,
    )

    tags = models.ManyToManyField("EventTag", related_name="events", blank=True)

    start_time = CustomDateTimeField(_("date et heure de début"), blank=False)
    end_time = CustomDateTimeField(_("date et heure de fin"), blank=False)
    timezone = models.CharField(
        "Fuseau horaire",
        max_length=255,
        choices=((name, name) for name in pytz.all_timezones),
        default=timezone.get_default_timezone().zone,
        blank=False,
        null=False,
    )

    max_participants = models.IntegerField(
        "Nombre maximum de participants", blank=True, null=True
    )
    allow_guests = models.BooleanField(
        "Autoriser les participant⋅e⋅s à inscrire des invité⋅e⋅s", default=False
    )
    facebook = FacebookEventField("Événement correspondant sur Facebook", blank=True)

    attendees = models.ManyToManyField(
        "people.Person", related_name="events", through="RSVP"
    )
    groups_attendees = models.ManyToManyField(
        "groups.SupportGroup", related_name="attended_event", through="GroupAttendee"
    )

    organizers = models.ManyToManyField(
        "people.Person", related_name="organized_events", through="OrganizerConfig"
    )
    organizers_groups = models.ManyToManyField(
        "groups.SupportGroup",
        related_name="organized_events",
        through="OrganizerConfig",
    )

    report_image = StdImageField(
        verbose_name=_("image de couverture"),
        blank=True,
        variations={"thumbnail": (400, 250), "banner": (1200, 400)},
        upload_to=report_image_path,
        help_text=_(
            "Cette image apparaîtra en tête de votre compte-rendu, et dans les partages que vous ferez du"
            " compte-rendu sur les réseaux sociaux."
        ),
    )

    report_content = DescriptionField(
        verbose_name=_("compte-rendu de l'événement"),
        blank=True,
        allowed_tags="allowed_tags",
        help_text=_(
            "Ajoutez un compte-rendu de votre événement. N'hésitez pas à inclure des photos."
        ),
    )

    report_summary_sent = models.BooleanField(
        "Le mail de compte-rendu a été envoyé", default=False
    )

    subscription_form = models.OneToOneField(
        "people.PersonForm",
        verbose_name="Formulaire d'inscription",
        related_name="subscription_form_event",
        related_query_name="subscription_form_event",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    volunteer_application_form = models.OneToOneField(
        "people.PersonForm",
        verbose_name="Formulaire d'appel à volontaires",
        help_text="Si un formulaire existe, son lien sera affiché sur la page de l'événement et dans les e-mails de "
        "confirmation de participation.",
        related_name="volunteer_application_form_event",
        related_query_name="volunteer_application_form_event",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    payment_parameters = JSONField(
        verbose_name=_("Paramètres de paiement"),
        null=True,
        blank=True,
        help_text=EVENT_PAYMENT_PARAMETERS_DOCUMENTATION,
    )

    lien_feuille_externe = models.URLField(
        verbose_name="Lien vers une feuille de calcul externe",
        help_text="Une feuille de calcul externe à mettre à jour avec les participants à l'événement.",
        blank=True,
    )

    scanner_event = models.IntegerField(
        "L'ID de l'événement sur le logiciel de tickets", blank=True, null=True
    )
    scanner_category = models.IntegerField(
        "La catégorie que doivent avoir les tickets sur scanner", blank=True, null=True
    )

    enable_jitsi = models.BooleanField("Activer la visio-conférence", default=False)

    participation_template = models.TextField(
        _("Template pour la page de participation"), blank=True, null=True
    )

    do_not_list = models.BooleanField(
        "Ne pas lister l'événement",
        default=False,
        help_text="L'événement n'apparaîtra pas sur la carte, ni sur le calendrier "
        "et ne sera pas cherchable via la recherche interne ou les moteurs de recherche.",
    )

    meta = JSONField(
        _("Informations supplémentaires."),
        default=dict,
        blank=True,
        encoder=CustomJSONEncoder,
    )

    FOR_USERS_ALL = "A"
    FOR_USERS_INSOUMIS = "I"
    FOR_USERS_2022 = "2"
    FOR_USERS_CHOICES = (
        (FOR_USERS_ALL, "Tous les utilisateurs"),
        (FOR_USERS_INSOUMIS, "Les insoumis⋅es"),
        (FOR_USERS_2022, "Les signataires « Nous Sommes Pour ! »"),
    )

    for_users = models.CharField(
        "Utilisateur⋅ices de la plateforme concerné⋅es par l'événement",
        default=FOR_USERS_ALL,
        max_length=1,
        blank=False,
        choices=FOR_USERS_CHOICES,
    )

    online_url = models.URLField(
        "Url de visio-conférence",
        default="",
        blank=True,
    )

    suggestion_segment = models.ForeignKey(
        to="mailing.Segment",
        verbose_name="Segment de suggestion",
        on_delete=models.SET_NULL,
        related_name="suggested_events",
        related_query_name="suggested_event",
        null=True,
        blank=True,
        help_text=("Segment des personnes auquel cet événement sera suggéré."),
    )

    attendant_notice = models.TextField(
        "Note pour les participants",
        null=False,
        blank=True,
        default="",
        help_text=(
            "Note montrée aux participants à un événements et est envoyé dans l'e-mail de confirmation de participation"
        ),
    )

    event_speakers = models.ManyToManyField(
        "event_requests.EventSpeaker",
        verbose_name="Intervenant·es",
        related_name="events",
        related_query_name="event",
        blank=True,
    )

    email_campaign = models.OneToOneField(
        "nuntius.Campaign",
        verbose_name="Campagne e-mail",
        related_name="event",
        related_query_name="event",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("événement")
        verbose_name_plural = _("événements")
        ordering = ("-start_time", "-end_time")
        permissions = (
            # DEPRECIATED: every_event was set up as a potential solution to Rest Framework django permissions
            # Permission class default behaviour of requiring both global permissions and object permissions before
            # allowing users. Was not used in the end.s
            ("every_event", _("Peut éditer tous les événements")),
            ("view_hidden_event", _("Peut voir les événements non publiés")),
        )
        indexes = (
            models.Index(
                fields=["start_time", "end_time"], name="events_datetime_index"
            ),
            models.Index(fields=["end_time"], name="events_end_time_index"),
            models.Index(
                fields=["start_time", "end_time", "id"], name="events_datetime_id_index"
            ),
        )

    def __str__(self):
        return f"{self.name} ({self.get_display_date()})"

    def __repr__(self):
        return f"{self.__class__.__name__}(id={str(self.pk)!r}, name={self.name!r})"

    def to_ics(self, text_only_description=False):
        url = front_url("view_event", args=[self.pk], auto_login=False)
        ics_event = ics.Event(
            uid=url,
            name=self.name,
            begin=self.start_time,
            end=self.end_time,
            created=self.created,
            last_modified=self.modified,
            location=self.short_address,
            categories=[self.subtype.get_type_display()],
            geo=self.coordinates,
            url=url,
        )
        ics_event.organizer = Organizer(
            email=self.contact_email, common_name=self.contact_name
        )

        if text_only_description:
            ics_event.description = textify(self.description) + " " + ics_event.url
        else:
            ics_event.description = self.description + f"<p>{ics_event.url}</p>"

        return ics_event

    def _get_participants_counts(self):
        self.all_attendee_count, self.confirmed_attendee_count = (
            self.__class__.objects.with_participants()
            .values_list("all_attendee_count", "confirmed_attendee_count")
            .get(id=self.id)
        )

    @property
    def event_speaker(self):
        """Deprecated single event_speaker property used for retro-compatibilty only"""
        return self.event_speakers.first()

    @property
    def participants(self):
        if not hasattr(self, "all_attendee_count"):
            self._get_participants_counts()

        return self.all_attendee_count

    @property
    def participants_confirmes(self):
        if not hasattr(self, "confirmed_attendee_count"):
            self._get_participants_counts()

        return self.confirmed_attendee_count

    def get_organizer_people(self):
        organizer_people = sum(
            [group.referents for group in self.organizers_groups.distinct()],
            list(self.organizers.all()),
        )
        return list(set(organizer_people))

    @property
    def type(self):
        return self.subtype.type

    @property
    def local_start_time(self):
        tz = pytz.timezone(self.timezone)
        return self.start_time.astimezone(tz)

    @property
    def local_end_time(self):
        tz = pytz.timezone(self.timezone)
        return self.end_time.astimezone(tz)

    def get_datestring(self):
        return formats.date_format(self.local_start_time, "DATE_FORMAT")

    def get_timestring(self, hide_default_tz=False):
        timestring = formats.time_format(self.local_start_time, "TIME_FORMAT")
        if not hide_default_tz or self.timezone != timezone.get_default_timezone_name():
            timestring += f" ({self.timezone})"
        return timestring

    def get_display_date(self, hide_default_tz=False):
        start_time = self.local_start_time
        end_time = self.local_end_time

        if start_time.date() == end_time.date():
            timestring = _("le {date}, de {start_hour} à {end_hour}").format(
                date=formats.date_format(start_time, "DATE_FORMAT"),
                start_hour=formats.time_format(start_time, "TIME_FORMAT"),
                end_hour=formats.time_format(end_time, "TIME_FORMAT"),
            )
        else:
            timestring = _(
                "du {start_date}, {start_time} au {end_date}, {end_time}"
            ).format(
                start_date=formats.date_format(start_time, "DATE_FORMAT"),
                start_time=formats.date_format(start_time, "TIME_FORMAT"),
                end_date=formats.date_format(end_time, "DATE_FORMAT"),
                end_time=formats.date_format(end_time, "TIME_FORMAT"),
            )

        if not hide_default_tz or self.timezone != timezone.get_default_timezone_name():
            timestring += f" ({self.timezone})"

        return timestring

    def get_simple_display_date(self, hide_default_tz=False):
        return _("le {date} à {time}").format(
            date=self.get_datestring(),
            time=self.get_timestring(hide_default_tz=hide_default_tz),
        )

    def is_past(self):
        return timezone.now() > self.end_time

    def is_current(self):
        return self.start_time < timezone.now() < self.end_time

    def clean(self):
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValidationError(
                {
                    "end_time": _(
                        "La date de fin de l'événement doit être postérieure à sa date de début."
                    )
                }
            )

    def get_price_display(self):
        if self.payment_parameters is None:
            return None

        base_price = self.payment_parameters.get("price", 0)
        min_price = base_price
        max_price = base_price

        for mapping in self.payment_parameters.get("mappings", []):
            prices = [m["price"] for m in mapping["mapping"]]
            min_price += min(prices)
            max_price += max(prices)

        if min_price == max_price == 0:
            if "free_pricing" in self.payment_parameters:
                return "Prix libre"
            else:
                return None

        if min_price == max_price:
            display = "{} €".format(floatformat(min_price / 100, 2))
        else:
            display = "de {} à {} €".format(
                floatformat(min_price / 100, 2), floatformat(max_price / 100, 2)
            )

        if "free_pricing" in self.payment_parameters:
            display += " + montant libre"

        return display

    @property
    def is_free(self):
        return self.payment_parameters is None

    @property
    def is_2022(self):
        return self.for_users == self.FOR_USERS_2022

    def get_price(self, submission_data: dict = None):
        price = self.payment_parameters.get("price", 0)

        if submission_data is None:
            return price

        for mapping in self.payment_parameters.get("mappings", []):
            values = [submission_data.get(field) for field in mapping["fields"]]

            d = {tuple(v for v in m["values"]): m["price"] for m in mapping["mapping"]}

            price += d[tuple(values)]

        if "free_pricing" in self.payment_parameters:
            field = self.payment_parameters["free_pricing"]
            price += max(0, int(submission_data.get(field, 0) * 100))

        return price

    def get_absolute_url(self):
        return front_url("view_event", args=[self.pk])

    def confirmation_note(self):
        if not self.subscription_form:
            return ""

        return format_html(
            self.subscription_form.confirmation_note,
        )

    def get_google_calendar_url(self):
        # https://github.com/InteractionDesignFoundation/add-event-to-calendar-docs/blob/master/services/google.md
        df = "%Y%m%dT%H%M00"
        start_time = self.local_start_time.strftime(df)
        end_time = self.local_end_time.strftime(df)

        details = f"{self.description}<p><a href={self.get_absolute_url()}>Page de l'événement</a></p>"
        if self.online_url:
            details += f"<p><a href={self.online_url}>Rejoindre en ligne</a></p>"

        query = {
            "action": "TEMPLATE",
            "ctz": self.timezone,
            "text": self.name,
            "dates": f"{start_time}/{end_time}",
            "location": self.short_address,
            "details": details,
            "sprop": f"website:{self.get_absolute_url()}",
        }

        return f"https://calendar.google.com/calendar/render?{urlencode(query)}&sprop=name:Action%20Populaire"

    def for_organizer_group_members_only(self):
        return self.subtype.for_organizer_group_members_only

    def can_rsvp(self, person):
        if not person:
            return False

        if not self.for_organizer_group_members_only():
            return True

        return (
            Membership.objects.active()
            .filter(
                person=person,
                supportgroup_id__in=self.organizers_groups.values_list("id", flat=True),
                membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER,
            )
            .exists()
        )

    def can_rsvp_as_group(self, person):
        if not person or self.for_organizer_group_members_only():
            return False

        return (
            person.memberships.active()
            .filter(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
            .exists()
        )

    def get_meta_image(self):
        if hasattr(self, "image") and self.image:
            return urljoin(settings.FRONT_DOMAIN, self.image.url)

        # Use content hash as cache key for the auto-generated meta image
        content = ":".join(
            (
                self.name,
                self.location_zip,
                self.location_city,
                str(self.coordinates),
                str(self.start_time),
            )
        )
        content_hash = hashlib.sha1(content.encode("utf-8")).hexdigest()[:8]

        return front_url(
            "view_og_image_event",
            kwargs={"pk": self.pk, "cache_key": content_hash},
            absolute=True,
        )

    def get_absolute_image_url(self, variation="banner"):
        if not self.image or not hasattr(self.image, variation):
            return None

        image = getattr(self.image, variation)
        event_image = self.image.storage.url(image.name)

        if not is_absolute_url(event_image):
            event_image = settings.FRONT_DOMAIN + event_image

        return event_image

    def get_page_schema(self):
        schema = {
            "@context": "http://schema.org",
            "@type": "Event",
            "name": sanitize_html(self.name),
            "startDate": self.local_start_time.isoformat(),
            "endDate": self.local_end_time.isoformat(),
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {
                "@type": "Place",
                "name": sanitize_html(self.location_name),
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": sanitize_html(
                        self.location_address1 + " " + self.location_address2
                    ),
                    "postalCode": sanitize_html(self.location_zip),
                    "addressLocality": sanitize_html(self.location_city),
                    "addressCountry": sanitize_html(self.location_country.name),
                },
            },
            "image": self.get_meta_image(),
            "description": str(html.textify(self.description)),
        }

        if self.visibility != Event.VISIBILITY_PUBLIC:
            schema["eventStatus"] = "https://schema.org/EventCancelled"

        if self.online_url:
            schema[
                "eventAttendanceMode"
            ] = "https://schema.org/MixedEventAttendanceMode"
            schema["location"] = [
                schema["location"],
                {"@type": "VirtualLocation", "url": self.online_url},
            ]

        organizer_group = self.organizers_groups.first()
        if organizer_group:
            schema["organizer"] = {
                "name": sanitize_html(organizer_group.name),
                "url": front_url(
                    "view_group", absolute=True, kwargs={"pk": organizer_group.pk}
                ),
            }

        return mark_safe(json.dumps(schema, indent=2))

    def add_organizer_group(self, group, person=None):
        from agir.events.actions import add_organizer_group

        return add_organizer_group(self, group, as_person=person)


class EventSubtype(BaseSubtype):
    TYPE_GROUP_MEETING = "G"
    TYPE_PUBLIC_MEETING = "M"
    TYPE_PUBLIC_ACTION = "A"
    TYPE_OTHER_EVENTS = "O"

    TYPE_CHOICES = (
        (TYPE_GROUP_MEETING, _("Réunion privée de groupe")),
        (TYPE_PUBLIC_MEETING, _("Événement public")),
        (TYPE_PUBLIC_ACTION, _("Action publique")),
        (TYPE_OTHER_EVENTS, _("Autre")),
    )

    TYPES_PARAMETERS = {
        TYPE_GROUP_MEETING: {"color": "#4a64ac", "icon_name": "comments"},
        TYPE_PUBLIC_MEETING: {"color": "#e14b35", "icon_name": "bullhorn"},
        TYPE_PUBLIC_ACTION: {"color": "#c2306c", "icon_name": "exclamation"},
        TYPE_OTHER_EVENTS: {"color": "#49b37d", "icon_name": "calendar"},
    }

    TYPE_DESCRIPTION = {
        TYPE_GROUP_MEETING: _(
            "Une réunion qui concerne principalement les membres du groupes, et non le public de"
            " façon générale. Par exemple, la réunion hebdomadaire du groupe, une réunion de travail,"
            " ou l'audition d'une association"
        ),
        TYPE_PUBLIC_MEETING: _(
            "Un événement ouvert à tous les publics, au-delà des membres du groupe, mais"
            " qui aura lieu dans un lieu privé. Par exemple, un événement public avec un orateur,"
            " une projection ou un concert."
        ),
        TYPE_PUBLIC_ACTION: _(
            "Une action qui se déroulera dans un lieu public et qui aura comme objectif principal"
            " d'aller à la rencontre ou d'atteindre des personnes extérieures à la FI"
        ),
        TYPE_OTHER_EVENTS: _(
            "Tout autre type d'événement qui ne rentre pas dans les catégories ci-dessus."
        ),
    }

    EVENT_SUBTYPE_REQUIRED_DOCUMENT_TYPE_CHOICES = [
        choice
        for choice in TypeDocument.choices
        if f"{TypeDocument.ATTESTATION}-" in choice[0]
    ]

    type = models.CharField(_("Type d'événement"), max_length=1, choices=TYPE_CHOICES)

    default_description = DescriptionField(
        verbose_name=_("description par défaut"),
        blank=True,
        help_text="La description par défaut pour les événements de ce sous-type.",
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
    )

    default_image = StdImageField(
        _("image par défaut"),
        upload_to=banner_image_file_path,
        variations=settings.BANNER_CONFIG,
        blank=True,
        help_text=_("L'image associée par défaut à un événement de ce sous-type."),
    )

    has_priority = models.BooleanField(
        "Le sous-type d'événement est prioritaire",
        default=False,
        help_text="Le sous-type d'événement apparaîtra en premier dans la liste des sous-types disponibles, "
        "par exemple lors de la création d'un événement.",
    )

    related_project_type = models.CharField(
        verbose_name="Type de projet de gestion associé",
        choices=TypeProjet.choices,
        max_length=10,
        blank=True,
        default="",
    )

    required_documents = ArrayField(
        verbose_name="Attestations requi" "ses",
        base_field=models.CharField(
            choices=EVENT_SUBTYPE_REQUIRED_DOCUMENT_TYPE_CHOICES,
            max_length=10,
        ),
        null=False,
        blank=False,
        default=list,
    )

    report_person_form = models.ForeignKey(
        "people.PersonForm",
        verbose_name="Formulaire de bilan",
        help_text="Les organisateur·ices des événements de ce type seront invité·es à remplir ce formulaire une fois "
        "l'événement terminé",
        related_name="event_subtype",
        related_query_name="event_subtype",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    is_editable = models.BooleanField(
        "Les événements de ce sous-type seront modifiables",
        default=True,
        help_text="Les événements de ce sous-type pourront être modifiés par les organisateur·ices, "
        "et non seulement par les administrateur·ices",
    )

    is_acceptable_for_group_certification = models.BooleanField(
        "Accepté pour la certification",
        default=True,
        help_text="Les événements récents de ce sous-type seront pris en compte (ou non) pour ouvrir "
        "le droit à un groupe d'action à la certification",
    )

    for_organizer_group_members_only = models.BooleanField(
        "Réservé aux membres des groupes organisateurs",
        default=False,
        help_text="Seulement les membres des groupes organisateurs pourront rejoindre les événements de ce type",
    )

    unauthorized_message = models.TextField(
        "Note pour les personnes non autorisées",
        blank=True,
        null=False,
        default="",
        help_text="Cette note sera affichée sur la page de l'événement aux personnes qui n'ont pas le droit "
        "de participer à un événement de ce type",
    )

    for_supportgroup_type = models.CharField(
        "Organisation réservé au type de groupe",
        max_length=1,
        null=True,
        blank=True,
        default=None,
        choices=SupportGroup.TYPE_CHOICES,
        help_text="Seulement les gestionnaires et animateur·ices des groupes du type sélectionné "
        "pourront créer des événements de ce type.",
    )

    is_coorganizable = models.BooleanField(
        "Co-organisation avec d'autres groupes d'action autorisée",
        default=True,
        help_text="Les organisateur·ices pourront inviter d'autres groupes d'action à co-organiser les "
        "événements de ce type.",
    )

    campaign_template = models.ForeignKey(
        "nuntius.Campaign",
        verbose_name="Modèle de campagne e-mail",
        related_name="event_subtypes",
        related_query_name="event_subytpe",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Si une campagne a été sélectionné, celle-ci pourra être utilisée comme modèle pour créer "
        "automatiquement une campagne pour un événement de ce type.",
    )

    class Meta:
        verbose_name = _("Sous-type d'événement")
        verbose_name_plural = _("Sous-types d'événement")
        ordering = ["-has_priority"]

    def __str__(self):
        return self.description


class EventTag(AbstractLabel):
    class Meta:
        verbose_name = "tag"


class CalendarManager(models.Manager):
    def create_calendar(self, name, slug=None, **kwargs):
        if slug is None:
            slug = slugify(name)

        return super().create(name=name, slug=slug, **kwargs)


class Calendar(ImageMixin):
    objects = CalendarManager()

    name = models.CharField(_("titre"), max_length=255)
    slug = models.SlugField(_("slug"), unique=True)
    archived = models.BooleanField("Calendrier archivé", default=False)

    parent = models.ForeignKey(
        "Calendar",
        on_delete=models.SET_NULL,
        related_name="children",
        related_query_name="child",
        null=True,
        blank=True,
    )
    events = models.ManyToManyField(
        "Event", related_name="calendars", through="CalendarItem"
    )

    user_contributed = models.BooleanField(
        _("Les utilisateurs peuvent ajouter des événements"), default=False
    )

    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("Saisissez une description (HTML accepté)"),
    )

    image = StdImageField(
        _("bannière"),
        upload_to=FilePattern(
            filename_pattern="{app_label}/{model_name}/{instance.name:slug}{ext}"
        ),
        variations={"thumbnail": (400, 250), "banner": (1200, 400)},
        blank=True,
    )

    class Meta:
        verbose_name = _("Agenda")

    def __str__(self):
        return self.name

    def clean_fields(self, exclude=None):
        super().clean_fields()

        if exclude is None:
            exclude = []

        if "parent" not in exclude:
            calendar = self
            for i in range(settings.CALENDAR_MAXIMAL_DEPTH):
                calendar = calendar.parent

                if calendar is None:
                    break
            else:
                raise ValidationError(
                    {
                        "parent": ValidationError(
                            _(
                                "Impossible d'utiliser ce calendrier comme parent :"
                                " cela excéderait la profondeur maximale autorisée."
                            )
                        )
                    }
                )


class CalendarItem(ExportModelOperationsMixin("calendar_item"), TimeStampedModel):
    event = models.ForeignKey(
        "Event", on_delete=models.CASCADE, related_name="calendar_items"
    )
    calendar = models.ForeignKey(
        "Calendar", on_delete=models.CASCADE, related_name="items"
    )

    class Meta:
        verbose_name = _("Élément de calendrier")


class GroupAttendee(ExportModelOperationsMixin("group_attendee"), TimeStampedModel):
    """
    Model that represents a group attendee to an event.
    """

    organizer = models.ForeignKey(
        "people.Person",
        related_name="group_event_participation",
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        "groups.supportgroup",
        related_name="group_participation",
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        "Event", related_name="event_participation", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "group_attendee"
        verbose_name = "Groupe participant"
        verbose_name_plural = "Groupes participants"
        unique_together = ("event", "group")

    def __str__(self):
        return "{group} participe à l'événement --> {event} | Par {organizer}".format(
            group=self.group, event=self.event, organizer=self.organizer
        )


class RSVP(ExportModelOperationsMixin("rsvp"), TimeStampedModel):
    """
    Model that represents a RSVP for one person for an event.

    An additional field indicates if the person is bringing any guests with her
    """

    STATUS_AWAITING_PAYMENT = "AP"
    STATUS_CONFIRMED = "CO"
    STATUS_CANCELED = "CA"
    STATUS_CHOICES = (
        (STATUS_AWAITING_PAYMENT, _("En attente du paiement")),
        (STATUS_CONFIRMED, _("Inscription confirmée")),
        (STATUS_CANCELED, _("Inscription annulée")),
    )

    objects = RSVPQuerySet.as_manager()

    person = models.ForeignKey(
        "people.Person", related_name="rsvps", on_delete=models.CASCADE, editable=False
    )
    event = models.ForeignKey(
        "Event", related_name="rsvps", on_delete=models.CASCADE, editable=False
    )
    guests = models.PositiveIntegerField(
        _("nombre d'invités supplémentaires"), default=0, null=False
    )

    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="rsvp",
    )
    form_submission = models.OneToOneField(
        "people.PersonFormSubmission",
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="rsvp",
    )
    guests_form_submissions = models.ManyToManyField(
        "people.PersonFormSubmission",
        related_name="guest_rsvp",
        through="IdentifiedGuest",
    )

    status = models.CharField(
        _("Statut"),
        max_length=2,
        default=STATUS_CONFIRMED,
        choices=STATUS_CHOICES,
        blank=False,
    )

    notifications_enabled = models.BooleanField(
        _("Recevoir les notifications"), default=True
    )

    jitsi_meeting = models.ForeignKey(
        "JitsiMeeting",
        related_name="rsvps",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "RSVP"
        verbose_name_plural = "RSVP"
        unique_together = ("event", "person")

    def __str__(self):
        info = "{person} --> {event} ({guests} invités)".format(
            person=self.person, event=self.event, guests=self.guests
        )

        if self.status == RSVP.STATUS_AWAITING_PAYMENT or any(
            guest.status == RSVP.STATUS_AWAITING_PAYMENT
            for guest in self.identified_guests.all()
        ):
            info = info + " paiement(s) en attente"

        return info


class IdentifiedGuest(ExportModelOperationsMixin("identified_guest"), models.Model):
    rsvp = models.ForeignKey(
        "RSVP", on_delete=models.CASCADE, null=False, related_name="identified_guests"
    )
    submission = models.OneToOneField(
        "people.PersonFormSubmission",
        on_delete=models.SET_NULL,
        null=True,
        db_column="personformsubmission_id",
        related_name="rsvp_guest",
    )
    status = models.CharField(
        _("Statut"),
        max_length=2,
        default=RSVP.STATUS_CONFIRMED,
        choices=RSVP.STATUS_CHOICES,
        blank=False,
    )
    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="identified_guest",
    )

    class Meta:
        db_table = "events_rsvp_guests_form_submissions"
        unique_together = ("rsvp", "submission")


class OrganizerConfig(ExportModelOperationsMixin("organizer_config"), models.Model):
    is_creator = models.BooleanField(_("Créateur de l'événement"), default=False)

    event = models.ForeignKey(
        "Event",
        related_name="organizer_configs",
        on_delete=models.CASCADE,
        editable=False,
    )

    person = models.ForeignKey(
        "people.Person",
        related_name="organizer_configs",
        on_delete=models.CASCADE,
        editable=False,
    )

    as_group = models.ForeignKey(
        "groups.SupportGroup",
        related_name="organizer_configs",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    notifications_enabled = models.BooleanField(
        _("Recevoir les notifications"), default=True
    )

    def clean(self):
        super().clean()
        if self.as_group is None:
            return

        if not self.as_group.memberships.filter(
            person=self.person,
            membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
        ).exists():
            raise ValidationError(
                {"as_group": "Le groupe doit être un groupe que vous gérez."}
            )


event_image_path = FilePattern(
    filename_pattern="events/event/{instance.event_id}/{uuid:s}{ext}"
)


class EventImage(ExportModelOperationsMixin("event_image"), TimeStampedModel):
    event = models.ForeignKey(
        "Event", on_delete=models.CASCADE, related_name="images", null=False
    )
    author = models.ForeignKey(
        "people.Person",
        related_name="event_images",
        on_delete=models.CASCADE,
        null=False,
        editable=False,
    )
    image = StdImageField(
        _("Fichier"),
        variations={"thumbnail": (200, 200, True), "admin_thumbnail": (100, 100, True)},
        render_variations=resize_and_autorotate,
        upload_to=event_image_path,
        null=False,
        blank=False,
    )
    legend = models.CharField(_("légende"), max_length=280)


def jitsi_default_domain():
    return random.choice(settings.JITSI_SERVERS)


def jitsi_default_room_name():
    return token_urlsafe(12).lower()


class JitsiMeeting(models.Model):
    domain = models.CharField(max_length=255, default=jitsi_default_domain)
    room_name = models.CharField(
        max_length=255,
        unique=True,
        default=jitsi_default_room_name,
        validators=[
            RegexValidator(
                re.compile(r"^[a-z0-9-_]+$"),
                "Seulement des lettres minuscules, des chiffres, des _ et des -.",
                "invalid",
            )
        ],
    )
    event = models.ForeignKey(
        "Event",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="jitsi_meetings",
    )
    start_time = models.DateTimeField("Début effectif", null=True, blank=True)
    end_time = models.DateTimeField("Fin effective", null=True, blank=True)

    @property
    def link(self):
        return "https://" + self.domain + "/" + self.room_name

    def __str__(self):
        return self.room_name

    class Meta:
        verbose_name = "Visio-conférence"


class Invitation(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REFUSED = "refused"

    STATUSES = (
        (STATUS_PENDING, "En attente"),
        (STATUS_ACCEPTED, "Acceptée"),
        (STATUS_REFUSED, "Refusée"),
    )

    person_sender = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        verbose_name="Personne qui émet l'invitation",
    )
    person_recipient = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="invitation_response",
        verbose_name="Personne qui répond à l'invitation",
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="Evenement de l'invitation",
    )
    group = models.ForeignKey(
        "groups.SupportGroup",
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="Groupe invité à l'événement",
    )
    status = models.CharField(
        "status",
        max_length=20,
        choices=STATUSES,
        default=STATUS_PENDING,
        null=False,
        blank=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "group"],
                name="unique",
            ),
        ]
