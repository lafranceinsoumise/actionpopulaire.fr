from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import BooleanField
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from agir.events.actions.rsvps import (
    rsvp_to_paid_event_and_create_payment,
    rsvp_to_free_event,
)
from agir.events.forms import BILLING_FIELDS
from agir.events.models import EventSubtype, RSVP
from agir.payments.models import Payment
from agir.payments.payment_modes import PaymentModeField, PAYMENT_MODES
from agir.people.models import Person
from agir.people.person_forms.forms import BasePersonForm
from .. import models
from ..apps import DEFAULT_ADMIN_MODES
from ..tasks import send_organizer_validation_notification
from ...gestion.typologies import TypeDocument
from ...lib.admin.form_fields import AutocompleteSelectModel
from ...lib.form_fields import AdminRichEditorWidget
from ...lib.forms import CoordinatesFormMixin


class CalendarIterator:
    """Simple iterator

    We cannot use a generator expression, because Django often needs to copy widgets (and thus
    choices iterators), and use pickling for that: however, generator expressions are not
    picklable.

    """

    def __init__(self, field):
        self.field = field

    def __iter__(self):
        return (
            (c.pk, self.field.label_from_instance(c)) for c in self.field.get_queryset()
        )


class CalendarField(forms.Field):
    widget = forms.CheckboxSelectMultiple
    default_error_messages = {
        "invalid_choice": "Choix invalide",
        "invalid_list": "Devrait être une liste",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widget.choices = CalendarIterator(self)
        self.widget.attrs["class"] = "widget-limit-max-height"

    def to_python(self, value):
        if value in self.empty_values:
            return []

        try:
            value = frozenset(str(c) for c in value)
        except TypeError:
            raise forms.ValidationError(
                self.error_messages["invalid_list"], "invalid_list"
            )

        queryset = self.get_queryset()
        ids = {str(c.pk) for c in queryset}
        for pk in value:
            if str(pk) not in ids:
                raise forms.ValidationError(
                    self.error_messages["invalid_choice"], params={"value": value}
                )

        return [c for c in queryset if str(c.pk) in value]

    def prepare_value(self, value):
        return [getattr(c, "pk", c) for c in value]

    def get_queryset(self):
        return models.Calendar.objects.raw(
            """
            WITH RECURSIVE calendars AS (
                SELECT id, name, 0 AS depth, slug::text AS path
                FROM events_calendar
                WHERE parent_id IS NULL AND archived = FALSE
              UNION ALL
                SELECT c.id, c.name, p.depth + 1 AS depth, CONCAT(p.path, ':', c.slug) AS path
                FROM events_calendar AS c
                JOIN calendars AS p
                ON parent_id = p.id
                WHERE c.archived = FALSE
            )
            SELECT id, name, depth
            FROM calendars
            ORDER BY path;
            """
        )

    def label_from_instance(self, obj):
        return (
            ((obj.depth - 1) * "\u2003" + "\u2ba1 ") if obj.depth else ""
        ) + obj.name


class EventAdminForm(CoordinatesFormMixin, forms.ModelForm):
    calendars = CalendarField(required=False, label="Agendas")

    subtype = forms.ModelChoiceField(
        label="Sous-type",
        queryset=EventSubtype.objects.filter(
            visibility__in=[EventSubtype.VISIBILITY_ADMIN, EventSubtype.VISIBILITY_ALL]
        ),
        initial=models.get_default_subtype,
    )

    send_visibility_notification = BooleanField(
        required=False,
        label="Envoyer une notification de changement de statut aux organisateurices",
        help_text=("Cela ne fonctionne qu'en cas de passage en visibilité publique"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["calendars"].initial = self.instance.calendars.all()

    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data.get("allow_guests")
            and cleaned_data.get("subscription_form") is not None
            and cleaned_data["subscription_form"].editable
        ):
            raise ValidationError(
                "Vous ne pouvez pas accepter des invités si les gens peuvent modifier leur "
                "inscription."
            )

        if self.cleaned_data["send_visibility_notification"] and (
            "visibility" not in self.changed_data
            or self.initial["visibility"] != models.Event.VISIBILITY_ORGANIZER
            or self.cleaned_data["visibility"] != models.Event.VISIBILITY_PUBLIC
        ):
            raise ValidationError(
                "Demande incorrecte : vous ne pouvez pas envoyer de notification pour ce type de modification. "
                "Rien n'a été enregistré, merci de recommencer."
            )

        return cleaned_data

    def save(self, commit=True, **kwargs):
        result = super().save(commit, **kwargs)
        if (
            self.cleaned_data["send_visibility_notification"]
            and "visibility" in self.changed_data
            and self.initial["visibility"] == models.Event.VISIBILITY_ORGANIZER
            and self.cleaned_data["visibility"] == models.Event.VISIBILITY_PUBLIC
        ):
            send_organizer_validation_notification.delay(self.instance.pk)

        return result

    def _save_m2m(self):
        super()._save_m2m()

        current_calendars = set(c.pk for c in self.instance.calendars.all())
        new_calendars = set(c.pk for c in self.cleaned_data["calendars"])

        # delete items for removed calendars
        models.CalendarItem.objects.filter(
            event=self.instance, calendar_id__in=current_calendars - new_calendars
        ).delete()

        # add items for added calendars
        models.CalendarItem.objects.bulk_create(
            models.CalendarItem(event=self.instance, calendar_id=c)
            for c in new_calendars - current_calendars
        )

    class Meta:
        exclude = ("id", "organizers", "attendees")
        widgets = {
            "description": AdminRichEditorWidget(),
            "report_content": AdminRichEditorWidget(),
        }

        help_texts = {
            "lien_feuille_externe": mark_safe(
                f"Google Sheet uniquement pour le moment. La feuille doit être partagée"
                f" en écriture avec l'utilisateur <em>{settings.GCE_ACCOUNT_EMAIL}</em>."
            )
        }


class AddOrganizerForm(forms.Form):
    person = forms.ModelChoiceField(
        Person.objects.all(), required=True, label=_("Personne à ajouter")
    )

    def __init__(self, event, model_admin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        self.fields["person"].widget = AutocompleteSelectModel(
            Person,
            admin_site=model_admin.admin_site,
            choices=self.fields["person"].choices,
        )

    def clean_person(self):
        person = self.cleaned_data["person"]
        if models.OrganizerConfig.objects.filter(
            person=person, event=self.event
        ).exists():
            raise forms.ValidationError(
                _("Cette personne organise déjà à cet événement")
            )

        return person

    def save(self):
        return models.OrganizerConfig.objects.create(
            person=self.cleaned_data["person"], event=self.event
        )


class NewParticipantForm(BasePersonForm):
    existing_person = forms.ModelChoiceField(
        label="Compte existant",
        queryset=Person.objects.all(),
        empty_label=_("None"),
        required=False,
    )

    new_person_email = forms.EmailField(
        label="ou si non-inscrit, email d'inscription", required=False
    )

    insoumise = forms.BooleanField(
        required=False,
        label="La personne souhaite recevoir les emails de la France insoumise",
        help_text="Ce champ ne s'applique que s'il s'agit de la création d'une nouvelle personne.",
    )

    payment_mode = PaymentModeField(required=True, payment_modes=DEFAULT_ADMIN_MODES)

    def __init__(self, *args, model_admin, event, **kwargs):
        super().__init__(*args, **kwargs)

        self.event = event

        self.fields["existing_person"].widget = AutocompleteSelectModel(
            Person,
            admin_site=model_admin.admin_site,
            choices=self.fields["existing_person"].choices,
        )

        if event.payment_parameters.get("admin_payment_modes"):
            self.fields["payment_mode"].payment_modes = event.payment_parameters[
                "admin_payment_modes"
            ]

        if "location_address2" in self.fields:
            self.fields["location_address2"].required = False

        self.fieldsets = [
            (
                "Compte",
                {"fields": ("existing_person", "new_person_email", "insoumise")},
            ),
            (
                "Informations d'inscription",
                {"fields": list(self.person_form_instance.fields_dict)},
            ),
        ]

    def clean_existing_person(self):
        existing_person = self.cleaned_data["existing_person"]

        if (
            existing_person is not None
            and RSVP.objects.filter(event=self.event, person=existing_person).exists()
        ):
            rsvp = (
                RSVP.objects.filter(event=self.event, person=existing_person)
                .select_related("payment")
                .get()
            )
            try:
                payment = rsvp.payment
                if payment is None:
                    raise Payment.DoesNotExist()
                message = format_html(
                    '{error_text} (<a href="{payment_link_url}">{payment_link_text}</a>)',
                    error_text="Cette personne participe déjà à l'événement",
                    payment_link_url=reverse(
                        "admin:payments_payment_change", args=[payment.pk]
                    ),
                    payment_link_text="voir son paiement",
                )
            except Payment.DoesNotExist:
                message = "Cette personne participe déjà à l'événement."

            raise ValidationError(message, code="already_rsvp")

        return existing_person

    def clean(self):
        if (
            "existing_person" in self.cleaned_data
            and self.cleaned_data["existing_person"] is not None
        ):
            self.data = self.data.dict()
            for f in self._meta.fields:
                if f not in self.cleaned_data:
                    self.data[f] = getattr(self.cleaned_data["existing_person"], f)

        return self.cleaned_data

    @property
    def submission_data(self):
        data = BasePersonForm.submission_data.fget(self)
        data["admin"] = True
        return data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data

        # si l'existing person existe, c'est elle qui doit être modifiée par le formulaire
        if cleaned_data["existing_person"] is not None:
            self.instance = cleaned_data["existing_person"]
        elif cleaned_data["new_person_email"]:
            try:
                self.instance = Person.objects.get_by_natural_key(
                    cleaned_data["new_person_email"]
                )
            except Person.DoesNotExist:
                pass

        if self.instance._state.adding:
            self.instance.is_insoumise = self.instance.subscribed = self.cleaned_data[
                "insoumise"
            ]

        # pour sauver l'instance, il faut appeler la méthode ModelForm plutôt que celle
        # de BasePersonForm parce que cette dernière ne crée jamais d'instance.
        with transaction.atomic():
            self.instance = forms.ModelForm.save(self, commit)
            self.submission = self.save_submission(self.instance)

            if cleaned_data["new_person_email"]:
                self.instance.add_email(cleaned_data["new_person_email"])

        return self.instance

    def free_rsvp(self):
        rsvp_to_free_event(self.event, self.instance, self.submission)

    def redirect_to_payment(self):
        payment = rsvp_to_paid_event_and_create_payment(
            self.event,
            self.instance,
            self.cleaned_data["payment_mode"],
            self.submission,
        )

        if self.cleaned_data["payment_mode"].can_admin:
            return HttpResponseRedirect(
                reverse("admin:payments_payment_change", args=(payment.id,))
            )

        return HttpResponseRedirect(payment.get_payment_url())

    class Meta:
        model = Person
        fields = BILLING_FIELDS


class EventSubtypeAdminForm(forms.ModelForm):
    required_documents = forms.MultipleChoiceField(
        label="Attestations requises",
        choices=(
            choice
            for choice in TypeDocument.choices
            if f"{TypeDocument.ATTESTATION}-" in choice[0]
        ),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["icon_name"].help_text = mark_safe(
            "Le nom de l'icône tout en minuscules et, optionnellement, "
            "le nom du style souhaité séparés par <code>:</code>&nbsp;: "
            "ex. <code>grill-hot</code>, <code>mustache:light</code> "
            '(cf. <a href="https://fontawesome.com/icons">https://fontawesome.com/icons</a>)'
        )
