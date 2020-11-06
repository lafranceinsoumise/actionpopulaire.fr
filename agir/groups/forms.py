from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Row, Field
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from functools import reduce
from operator import or_

from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.groups.tasks import (
    send_support_group_changed_notification,
    send_support_group_creation_notification,
    send_external_join_confirmation,
    invite_to_group,
)
from agir.lib.form_components import *
from agir.lib.form_mixins import (
    LocationFormMixin,
    ContactFormMixin,
    GeocodingBaseForm,
    SearchByZipCodeFormBase,
    ImageFormMixin,
)
from agir.lib.tasks import geocode_support_group
from agir.people.models import Person

__all__ = [
    "SupportGroupForm",
    "AddReferentForm",
    "AddManagerForm",
    "InvitationForm",
    "GroupGeocodingForm",
    "SearchGroupForm",
]


class SupportGroupForm(
    LocationFormMixin, ContactFormMixin, ImageFormMixin, forms.ModelForm
):
    geocoding_task = geocode_support_group

    CHANGES = {
        "name": "information",
        "contact_email": "contact",
        "contact_phone": "contact",
        "contact_hide_phone": "contact",
        "location_name": "location",
        "location_address1": "location",
        "location_address2": "location",
        "location_city": "location",
        "location_zip": "location",
        "location_country": "location",
        "description": "information",
    }

    image_field = "image"

    subtypes = forms.ModelMultipleChoiceField(
        queryset=SupportGroupSubtype.objects.filter(
            visibility=SupportGroupSubtype.VISIBILITY_ALL
        ),
        to_field_name="label",
    )

    def __init__(self, *args, person, **kwargs):
        super(SupportGroupForm, self).__init__(*args, **kwargs)

        self.person = person
        self.is_creation = self.instance._state.adding
        excluded_fields = set()

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Sauvegarder et publier"))

        # do not allow random organizers to modify HTML
        if self.instance.allow_html:
            del self.fields["description"]
            description_field = []
        else:
            description_field = [Row(FullCol("description"))]

        if not self.is_creation:
            self.fields["notify"] = forms.BooleanField(
                required=False,
                initial=False,
                label=_("Signalez ces changements aux membres du groupe"),
                help_text=_(
                    "Un email sera envoyé à la validation de ce formulaire. Merci de ne pas abuser de cette"
                    " fonctionnalité."
                ),
            )
            del self.fields["type"]
            del self.fields["subtypes"]
            notify_field = [Row(FullCol("notify"))]

            excluded_fields = reduce(
                or_,
                (
                    set(subtype.config.get("excluded_fields", []))
                    for subtype in self.instance.subtypes.all()
                ),
                set(),
            )

            if "image" in excluded_fields:
                excluded_fields.add("image_accept_license")

            for f in excluded_fields & set(self.fields):
                del self.fields[f]

        else:
            notify_field = []

        self.helper.layout = Layout(
            Row(FullCol("name")),
            Row(FullCol("image")),
            Row(FullCol("image_accept_license")),
            Section(
                _("Informations de contact"),
                Row(Div("contact_name", css_class="col-md-12")),
                Row(
                    HalfCol("contact_email", css_class="col-md-6"),
                    HalfCol(
                        "contact_phone", "contact_hide_phone", css_class="col-md-6"
                    ),
                ),
            ),
            Section(
                _("Lieu"),
                Row(
                    HTML(
                        "<p><b>Merci d'indiquer une adresse précise avec numéro de rue, sans quoi le groupe"
                        " n'apparaîtra pas sur la carte.</b>"
                        " Si les réunions se déroulent chez vous et que vous ne souhaitez pas rendre cette adresse"
                        " publique, vous pouvez indiquer un endroit à proximité, comme un café, ou votre mairie."
                    ),
                    css_class="col-xs-12",
                ),
                Row(FullCol("location_name")),
                Row(
                    FullCol(
                        Field("location_address1", placeholder=_("1ère ligne")),
                        Field("location_address2", placeholder=_("2ème ligne")),
                    )
                ),
                Row(
                    Div("location_zip", css_class="col-md-4"),
                    Div("location_city", css_class="col-md-8"),
                ),
                Row(FullCol("location_country")),
            ),
            *description_field,
            *notify_field,
        )

        remove_excluded_field_from_layout(self.helper.layout, excluded_fields)

    def save(self, commit=True):
        res = super().save(commit=commit)

        if commit:
            self.schedule_tasks()

        return res

    def _save_m2m(self):
        super()._save_m2m()
        if self.is_creation:
            self.membership = Membership.objects.create(
                person=self.person,
                supportgroup=self.instance,
                membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
            )

    def schedule_tasks(self):
        super().schedule_tasks()

        # create set so that values are unique, but turns to list because set are not JSON-serializable
        changes = list(
            {
                self.CHANGES[field]
                for field in self.changed_data
                if field in self.CHANGES
            }
        )

        # if it's a new group creation, send the confirmation notification and geolocate it
        if self.is_creation:
            # membership attribute created by _save_m2m
            send_support_group_creation_notification.delay(self.membership.pk)
        else:
            # send changes notification if the notify checkbox was checked
            if changes and self.cleaned_data.get("notify"):
                send_support_group_changed_notification.delay(self.instance.pk, changes)

    class Meta:
        model = SupportGroup
        fields = (
            "name",
            "image",
            "type",
            "subtypes",
            "contact_name",
            "contact_email",
            "contact_phone",
            "contact_hide_phone",
            "location_name",
            "location_address1",
            "location_address2",
            "location_city",
            "location_zip",
            "location_country",
            "description",
        )


class MembershipChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.person)


class AddReferentForm(forms.Form):
    form = forms.CharField(initial="add_referent_form", widget=forms.HiddenInput())
    referent = MembershipChoiceField(
        queryset=Membership.objects.filter(
            membership_type__lt=Membership.MEMBERSHIP_TYPE_REFERENT
        ),
        label=_("Second animateur"),
    )

    def __init__(self, support_group, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["referent"].queryset = self.fields["referent"].queryset.filter(
            supportgroup=support_group
        )

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Signaler comme second animateur")))

    def perform(self):
        membership = self.cleaned_data["referent"]

        membership.membership_type = Membership.MEMBERSHIP_TYPE_REFERENT
        membership.save()

        return {"email": membership.person.email}


class AddManagerForm(forms.Form):
    form = forms.CharField(initial="add_manager_form", widget=forms.HiddenInput())
    manager = MembershipChoiceField(
        queryset=Membership.objects.filter(
            membership_type__lt=Membership.MEMBERSHIP_TYPE_MANAGER
        ),
        label=False,
    )

    def __init__(self, support_group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_group = support_group

        self.fields["manager"].queryset = self.fields["manager"].queryset.filter(
            supportgroup=support_group
        )

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Ajouter comme membre gestionnaire")))

    def perform(self):
        membership = self.cleaned_data["manager"]

        membership.membership_type = max(
            membership.membership_type, Membership.MEMBERSHIP_TYPE_MANAGER
        )
        membership.save()

        return {"email": membership.person.email}


class InvitationForm(forms.Form):
    form = forms.CharField(initial="invitation_form", widget=forms.HiddenInput())
    email = forms.EmailField(label="L'adresse email de la personne à inviter")

    def __init__(self, *args, group, inviter, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.inviter = inviter

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Inviter")))

    def clean_email(self):
        try:
            p = Person.objects.get_by_natural_key(self.cleaned_data["email"])
            Membership.objects.get(supportgroup=self.group, person=p)
        except (Person.DoesNotExist, Membership.DoesNotExist):
            pass
        else:
            raise ValidationError("Cette personne fait déjà partie de votre groupe !")

        return self.cleaned_data["email"]

    def perform(self):
        invite_to_group.delay(
            str(self.group.id), self.cleaned_data["email"], str(self.inviter.id)
        )
        return {"email": self.cleaned_data["email"]}


class GroupGeocodingForm(GeocodingBaseForm):
    geocoding_task = geocode_support_group
    messages = {
        "use_geocoding": _(
            "La localisation de votre groupe sur la carte va être réinitialisée à partir de son adresse."
            " Patientez quelques minutes pour voir la nouvelle localisation apparaître."
        ),
        "coordinates_updated": _(
            "La localisation de votre groupe a été correctement mise à jour. Patientez quelques"
            " minutes pour la voir apparaître sur la carte."
        ),
    }

    class Meta:
        model = SupportGroup
        fields = ("coordinates",)


class SearchGroupForm(SearchByZipCodeFormBase):
    pass


class ExternalJoinForm(forms.Form):
    email = forms.EmailField()

    def send_confirmation_email(self, event):
        send_external_join_confirmation.delay(event.pk, **self.cleaned_data)


class InvitationWithSubscriptionConfirmationForm(forms.Form):
    location_zip = forms.CharField(
        label="Mon code postal",
        required=True,
        help_text=_(
            "Votre code postal nous permet de savoir dans quelle ville vous habitez, pour pouvoir vous proposer"
            " des informations locales."
        ),
    )

    join_support_group = forms.BooleanField(
        label=_("Je souhaite rejoindre le groupe d'action qui m'a invité"),
        help_text=_(
            "Vous pouvez aussi rejoindre la France insoumise sans rejoindre aucun groupe d'action en particulier."
        ),
        required=False,
        initial=True,
    )

    subscribed = forms.BooleanField(
        label="Je souhaite être tenu au courant de l'actualité de la France insoumise",
        required=False,
        help_text=_(
            "Si vous le souhaitez, nous pouvons vous envoyer notre lettre d'information hebdomadaire, et des"
            " informations locales."
        ),
    )

    def __init__(self, *args, email, group, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = email
        self.group = group

        if group is None:
            del self.fields["join_support_group"]

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Confirmer")))

    def save(self):
        cleaned_data = self.cleaned_data
        p = Person.objects.create_insoumise(
            email=self.email,
            subscribed=cleaned_data["subscribed"],
            subscribed_sms=cleaned_data["subscribed"],
            location_zip=cleaned_data["location_zip"],
            location_country="FR",
        )

        if cleaned_data.get("join_support_group"):
            Membership.objects.create(person=p, supportgroup=self.group)

        return p
