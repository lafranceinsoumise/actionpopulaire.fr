from functools import reduce, partial
from operator import or_

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Row, Field
from django import forms
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from agir.groups.actions.transfer import (
    schedule_membership_transfer_tasks,
)
from agir.groups.models import (
    SupportGroup,
    Membership,
    SupportGroupSubtype,
    TransferOperation,
)
from agir.groups.tasks import (
    send_support_group_changed_notification,
    send_support_group_creation_notification,
    create_group_creation_confirmation_activity,
    create_accepted_invitation_member_activity,
    geocode_support_group,
)
from agir.lib.form_components import *
from agir.lib.form_fields import RemoteSelectizeWidget
from agir.lib.form_mixins import (
    LocationFormMixin,
    ContactFormMixin,
    GeocodingBaseForm,
    SearchByZipCodeFormBase,
    ImageFormMixin,
)
from agir.people.models import Person

__all__ = [
    "SupportGroupForm",
    "GroupGeocodingForm",
    "SearchGroupForm",
    "TransferGroupMembersForm",
    "InvitationWithSubscriptionConfirmationForm",
]


class SupportGroupForm(
    LocationFormMixin, ContactFormMixin, ImageFormMixin, forms.ModelForm
):
    geocoding_task = geocode_support_group

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
            del self.fields["type"]
            del self.fields["subtypes"]

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

        # if it's a new group creation, send the confirmation notification and geolocate it
        if self.is_creation:
            # membership attribute created by _save_m2m
            send_support_group_creation_notification.delay(self.membership.pk)
            create_group_creation_confirmation_activity.delay(self.membership.pk)
        else:
            # send changes notification
            if self.changed_data:
                send_support_group_changed_notification.delay(
                    self.instance.pk, self.changed_data
                )

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


class MembershipMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return str(obj.person)


class SupportGroupChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj)


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
            membership, created = Membership.objects.get_or_create(
                supportgroup=self.group, person=p
            )
            if created:
                create_accepted_invitation_member_activity.delay(membership.pk)

        return p


class TransferGroupMembersForm(forms.Form):
    target_group = SupportGroupChoiceField(
        queryset=SupportGroup.objects.active(),
        label=_("Groupe de destination"),
        required=True,
        help_text="Le nouveau groupe doit avoir déjà été créé pour pouvoir y transférer une partie de vos membres.",
    )
    members = MembershipMultipleChoiceField(
        queryset=Membership.objects.all(),
        label=_("Membres à transférer"),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text="Les membres sélectionnés seront transférés dans le groupe de destination. Ses animateur·ices et les membres transférés recevront alors un e-mail de confirmation. Cette action est irréversible.",
    )

    def __init__(self, manager, former_group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.former_group = former_group
        self.manager = manager

        supportgroup_members = Membership.objects.filter(
            supportgroup=former_group
        ).exclude(person=manager)

        self.fields["members"].queryset = self.fields[
            "members"
        ].queryset = supportgroup_members

        base_query = {"exclude": former_group.pk}

        self.fields["target_group"].widget = RemoteSelectizeWidget(
            api_url=reverse_lazy("legacy_api_search_group"),
            label_field="name",
            value_field="id",
            base_query=base_query,
        )

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", _("Valider le transfert")))

    def save(self):
        cleaned_data = self.cleaned_data
        target_group = cleaned_data["target_group"]
        memberships = cleaned_data["members"]

        with transaction.atomic():
            transfer_operation = TransferOperation.objects.create(
                former_group=self.former_group,
                new_group=target_group,
                manager=self.manager,
            )
            transfer_operation.members.add(*(m.person for m in memberships))
            new_memberships = (
                Membership(
                    person=membership.person,
                    supportgroup=target_group,
                    membership_type=membership.membership_type,
                )
                for membership in memberships
            )
            Membership.objects.bulk_create(new_memberships, ignore_conflicts=True)
            memberships.delete()

            transaction.on_commit(
                partial(
                    schedule_membership_transfer_tasks,
                    transfer_operation,
                )
            )

        return {
            "target_group": target_group,
            "transferred_memberships": transfer_operation.members,
        }
