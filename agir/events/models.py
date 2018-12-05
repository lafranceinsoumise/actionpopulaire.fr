import ics
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, Sum, Count, When, CharField, F, Q
from django.db.models.functions import Coalesce
from django.template.defaultfilters import floatformat
from django.utils import formats, timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django_prometheus.models import ExportModelOperationsMixin
from dynamic_filenames import FilePattern
from model_utils.models import TimeStampedModel

from stdimage.models import StdImageField
from slugify import slugify

from agir.lib.utils import front_url, resize_and_autorotate
from ..lib.models import (
    BaseAPIResource,
    AbstractLabel,
    NationBuilderResource,
    ContactMixin,
    LocationMixin,
    ImageMixin,
    DescriptionMixin,
    DescriptionField,
    AbstractMapObjectLabel,
)
from ..lib.form_fields import DateTimePickerWidget


class EventQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published=True)

    def upcoming(self, as_of=None, published_only=True):
        if as_of is None:
            as_of = timezone.now()

        condition = models.Q(end_time__gte=as_of)
        if published_only:
            condition &= models.Q(published=True)

        return self.filter(condition)

    def past(self, as_of=None, published_only=True):
        if as_of is None:
            as_of = timezone.now()

        condition = models.Q(end_time__lt=as_of)
        if published_only:
            condition &= models.Q(published=True)
        return self.filter(condition)

    def with_participants(self):
        confirmed_guests = Q(rsvps__identified_guests__status=RSVP.STATUS_CONFIRMED)
        confirmed_rsvps = Q(rsvps__status=RSVP.STATUS_CONFIRMED)

        return self.annotate(
            all_attendee_count=Case(
                When(
                    subscription_form=None,
                    then=Coalesce(Sum("rsvps__guests") + Count("rsvps"), 0),
                ),
                default=Coalesce(Count("rsvps__identified_guests") + Count("rsvps"), 0),
                output_field=CharField(),
            )
        ).annotate(
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
            )
        )


class RSVPQuerySet(models.QuerySet):
    def upcoming(self, as_of=None, published_only=True):
        if as_of is None:
            as_of = timezone.now()

        condition = models.Q(event__end_time__gte=as_of)
        if published_only:
            condition &= models.Q(event__published=True)

        return self.filter(condition)

    def past(self, as_of=None, published_only=True):
        if as_of is None:
            as_of = timezone.now()

        condition = models.Q(event__end_time__lt=as_of)
        if published_only:
            condition &= models.Q(event__published=True)

        return self.filter(condition)


class CustomDateTimeField(models.DateTimeField):
    def formfield(self, **kwargs):
        defaults = {"widget": DateTimePickerWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


def get_default_subtype():
    return (
        EventSubtype.objects.filter(type=EventSubtype.TYPE_PUBLIC_ACTION)
        .order_by("created")
        .values("id")
        .first()["id"]
    )


report_image_path = FilePattern(
    filename_pattern="{app_label}/{model_name}/{instance.id}/report_banner{ext}"
)


class Event(
    ExportModelOperationsMixin("event"),
    BaseAPIResource,
    NationBuilderResource,
    LocationMixin,
    ImageMixin,
    DescriptionMixin,
    ContactMixin,
):
    """
    Model that represents an event
    """

    objects = EventQuerySet.as_manager()

    name = models.CharField(
        _("nom"), max_length=255, blank=False, help_text=_("Le nom de l'événement")
    )

    published = models.BooleanField(
        _("publié"),
        default=True,
        help_text=_("L'évenement doit-il être visible publiquement."),
    )

    subtype = models.ForeignKey(
        "EventSubtype",
        verbose_name="Sous-type",
        related_name="events",
        on_delete=models.PROTECT,
        default=get_default_subtype,
    )

    nb_path = models.CharField(_("NationBuilder path"), max_length=255, blank=True)

    tags = models.ManyToManyField("EventTag", related_name="events", blank=True)

    start_time = CustomDateTimeField(_("date et heure de début"), blank=False)
    end_time = CustomDateTimeField(_("date et heure de fin"), blank=False)
    max_participants = models.IntegerField(
        "Nombre maximum de participants", blank=True, null=True
    )
    allow_guests = models.BooleanField(
        "Autoriser les participant⋅e⋅s à inscrire des invité⋅e⋅s", default=False
    )

    attendees = models.ManyToManyField(
        "people.Person", related_name="events", through="RSVP"
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

    subscription_form = models.ForeignKey(
        "people.PersonForm", null=True, blank=True, on_delete=models.PROTECT
    )
    payment_parameters = JSONField(
        verbose_name=_("Paramètres de paiement"), null=True, blank=True
    )

    scanner_event = models.IntegerField(
        "L'ID de l'événement sur le logiciel de tickets", blank=True, null=True
    )
    scanner_category = models.IntegerField(
        "La catégorie que doivent avoir les tickets sur scanner", blank=True, null=True
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
            models.Index(fields=["nb_path"], name="events_nb_path_index"),
        )

    def __str__(self):
        return self.name

    def to_ics(self):
        event_url = front_url("view_event", args=[self.pk], auto_login=False)
        return ics.Event(
            name=self.name,
            begin=self.start_time,
            end=self.end_time,
            uid=str(self.pk),
            description=self.description + f"<p>{event_url}</p>",
            location=self.short_address,
            url=event_url,
        )

    @property
    def participants(self):
        try:
            return self.all_attendee_count
        except AttributeError:
            if self.subscription_form:
                return (
                    self.rsvps.annotate(
                        identified_guests_count=Count("identified_guests")
                    ).aggregate(participants=Sum(F("identified_guests_count") + 1))[
                        "participants"
                    ]
                    or 0
                )
            return (
                self.rsvps.aggregate(participants=Sum(models.F("guests") + 1))[
                    "participants"
                ]
                or 0
            )

    @property
    def type(self):
        return self.subtype.type

    def get_display_date(self):
        tz = timezone.get_current_timezone()
        start_time = self.start_time.astimezone(tz)
        end_time = self.end_time.astimezone(tz)

        if start_time.date() == end_time.date():
            date = formats.date_format(start_time, "DATE_FORMAT")
            return _("le {date}, de {start_hour} à {end_hour}").format(
                date=date,
                start_hour=formats.time_format(start_time, "TIME_FORMAT"),
                end_hour=formats.time_format(end_time, "TIME_FORMAT"),
            )

        return _("du {start_date}, {start_time} au {end_date}, {end_time}").format(
            start_date=formats.date_format(start_time, "DATE_FORMAT"),
            start_time=formats.date_format(start_time, "TIME_FORMAT"),
            end_date=formats.date_format(end_time, "DATE_FORMAT"),
            end_time=formats.date_format(end_time, "TIME_FORMAT"),
        )

    def is_past(self):
        return timezone.now() > self.end_time

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

    def get_price(self, submission_data: dict = None):
        price = self.payment_parameters.get("price", 0)

        if submission_data is None:
            return price

        for mapping in self.payment_parameters.get("mappings", []):
            values = [submission_data.get(field) for field in mapping["fields"]]

            d = {tuple(v for v in m["values"]): m["price"] for m in mapping["mapping"]}

            price += d.get(tuple(values), 0)

        if "free_pricing" in self.payment_parameters:
            field = self.payment_parameters["free_pricing"]
            price += max(0, int(submission_data.get(field, 0) * 100))

        return price


class EventSubtype(AbstractMapObjectLabel):
    TYPE_GROUP_MEETING = "G"
    TYPE_PUBLIC_MEETING = "M"
    TYPE_PUBLIC_ACTION = "A"
    TYPE_OTHER_EVENTS = "O"

    TYPE_CHOICES = (
        (TYPE_GROUP_MEETING, _("Réunion de groupe")),
        (TYPE_PUBLIC_MEETING, _("Réunion publique")),
        (TYPE_PUBLIC_ACTION, _("Action publique")),
        (TYPE_OTHER_EVENTS, _("Autres type d'événements")),
    )

    type = models.CharField(_("Type d'événement"), max_length=1, choices=TYPE_CHOICES)
    allow_external = models.BooleanField(
        _("Les non-insoumis⋅es peuvent rejoindre"), default=False
    )
    external_help_text = models.TextField(
        _("Phrase d'explication pour rejoindre le groupe"), blank=True
    )

    class Meta:
        verbose_name = _("Sous-type d'événement")
        verbose_name_plural = _("Sous-types d'événement")

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


class Calendar(NationBuilderResource, ImageMixin):
    objects = CalendarManager()

    name = models.CharField(_("titre"), max_length=255)
    slug = models.SlugField(_("slug"))

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
    submission = models.ForeignKey(
        "people.PersonFormSubmission",
        on_delete=models.SET_NULL,
        null=True,
        db_column="personformsubmission_id",
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
    person = models.ForeignKey(
        "people.Person",
        related_name="organizer_configs",
        on_delete=models.CASCADE,
        editable=False,
    )
    event = models.ForeignKey(
        "Event",
        related_name="organizer_configs",
        on_delete=models.CASCADE,
        editable=False,
    )

    is_creator = models.BooleanField(_("Créateur de l'événement"), default=False)
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
        memberships = self.person.memberships.filter(is_manager=True).select_related(
            "supportgroup"
        )
        managed_groups = [membership.supportgroup for membership in memberships]
        if self.as_group and self.as_group not in managed_groups:
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
