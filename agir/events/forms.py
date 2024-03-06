from crispy_forms import layout
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Row
from django import forms
from django.template.defaultfilters import floatformat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from agir.lib.form_components import *
from agir.lib.form_mixins import (
    GeocodingBaseForm,
)
from agir.payments.payment_modes import PaymentModeField
from .models import Event, OrganizerConfig, EventImage
from .tasks import (
    send_external_rsvp_confirmation,
    geocode_event,
)
from ..lib.form_fields import AcceptCreativeCommonsLicenceField
from ..people.models import Person, PersonFormSubmission

__all__ = [
    "AddOrganizerForm",
    "EventGeocodingForm",
    "UploadEventImageForm",
    "AuthorForm",
    "BillingForm",
    "GuestsForm",
    "BaseRSVPForm",
    "ExternalRSVPForm",
]

# encodes the preferred order when showing the messages
NOTIFIED_CHANGES = {
    "name": "information",
    "start_time": "timing",
    "end_time": "timing",
    "contact_name": "contact",
    "contact_email": "contact",
    "contact_phone": "contact",
    "location_name": "location",
    "location_address1": "location",
    "location_address2": "location",
    "location_city": "location",
    "location_zip": "location",
    "location_country": "location",
    "description": "information",
    "facebook": "information",
}


class AgendaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class RSVPChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.person)


class AddOrganizerForm(forms.Form):
    form = forms.CharField(initial="add_organizer_form", widget=forms.HiddenInput())

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

        self.fields["organizer"] = RSVPChoiceField(
            queryset=event.rsvps.exclude(person__organized_events=event), label=False
        )

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Ajouter comme co-organisateur")))

    def save(self, commit=True):
        rsvp = self.cleaned_data["organizer"]

        organizer_config = OrganizerConfig(event=rsvp.event, person=rsvp.person)

        if commit:
            organizer_config.save()

        return organizer_config


class EventGeocodingForm(GeocodingBaseForm):
    geocoding_task = geocode_event
    messages = {
        "use_geocoding": _(
            "La localisation de votre événement sur la carte va être réinitialisée à partir de son adresse."
            " Patientez quelques minutes pour voir la nouvelle localisation apparaître."
        ),
        "coordinates_updated": _(
            "La localisation de votre événement a été correctement mise à jour. Patientez quelques"
            " minutes pour la voir apparaître sur la carte."
        ),
    }

    class Meta:
        model = Event
        fields = ("coordinates",)


class UploadEventImageForm(forms.ModelForm):
    accept_license = AcceptCreativeCommonsLicenceField(required=True)

    def __init__(self, *args, author=None, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        if author is not None:
            self.instance.author = author
        if event is not None:
            self.instance.event = event

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Ajouter mon image")))
        self.helper.form_tag = False
        self.helper.layout = Layout("image", "accept_license", "legend")

    class Meta:
        model = EventImage
        fields = ("image", "legend")


class AuthorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].required = self.fields["last_name"].required = True
        self.fields["last_name"].help_text = _(
            """
        Nous avons besoin de votre nom pour pouvoir vous identifier comme l'auteur de l'image.
        """
        )

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("first_name", "last_name")

    class Meta:
        model = Person
        fields = ("first_name", "last_name")


BILLING_FIELDS = (
    "first_name",
    "last_name",
    "location_address1",
    "location_address2",
    "location_zip",
    "location_city",
    "location_country",
    "contact_phone",
)


class BillingForm(forms.ModelForm):
    # these fields are used to make sure there's no problem if user starts paying several events at the same time
    event = forms.ModelChoiceField(
        Event.objects.all(), required=True, widget=forms.HiddenInput
    )
    submission = forms.ModelChoiceField(
        PersonFormSubmission.objects.all(), widget=forms.HiddenInput, required=False
    )
    payment_mode = PaymentModeField(
        required=True, payment_modes=["system_pay", "check_events"]
    )
    is_guest = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, event, submission, is_guest, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["submission"].initial = submission
        self.fields["event"].initial = event
        self.fields["is_guest"].initial = is_guest

        if event.payment_parameters.get("payment_modes"):
            self.fields["payment_mode"].payment_modes = event.payment_parameters[
                "payment_modes"
            ]

        # le moment où on stoppe les chèques peut être configuré par événement
        allow_checks_upto = event.payment_parameters.get("allow_checks_upto", 7)
        if event.start_time - timezone.now() < timezone.timedelta(
            days=allow_checks_upto
        ):
            self.fields["payment_mode"].payment_modes = [
                p
                for p in self.fields["payment_mode"].payment_modes
                if p.category != "check"
            ]

        for f in [
            "first_name",
            "last_name",
            "location_address1",
            "location_zip",
            "location_city",
            "location_country",
            "contact_phone",
        ]:
            self.fields[f].required = True
        self.fields["location_address1"].label = "Adresse"
        self.fields["location_address2"].label = False

        fields = ["submission", "event", "is_guest"]

        fields.extend(["first_name", "last_name"])
        fields.extend(
            [
                layout.Field("location_address1", placeholder="Ligne 1"),
                layout.Field("location_address2", placeholder="Ligne 2"),
            ]
        )

        fields.append(
            Row(
                layout.Div("location_zip", css_class="col-md-4"),
                layout.Div("location_city", css_class="col-md-8"),
            )
        )

        fields.append("location_country")
        fields.append("contact_phone")

        fields.append("payment_mode")

        self.helper = FormHelper()
        self.helper.add_input(
            layout.Submit(
                "valider",
                f"Je paie {floatformat(event.get_price(submission and submission.data)/100, 2)} €",
            )
        )
        self.helper.layout = layout.Layout(*fields)

    class Meta:
        model = Person
        fields = BILLING_FIELDS


class GuestsForm(forms.Form):
    guests = forms.IntegerField()


class BaseRSVPForm(forms.Form):
    is_guest = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, is_guest=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["is_guest"].initial = is_guest
        self.helper.layout.append("is_guest")


class ExternalRSVPForm(forms.Form):
    email = forms.EmailField()

    def send_confirmation_email(self, event):
        send_external_rsvp_confirmation.delay(event.pk, **self.cleaned_data)
