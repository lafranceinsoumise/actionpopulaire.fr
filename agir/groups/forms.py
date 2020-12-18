from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Row, Field
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from functools import reduce
from operator import or_

from agir.groups.models import (
    SupportGroup,
    Membership,
    SupportGroupSubtype,
    TranferOperation,
)
from agir.groups.tasks import (
    send_support_group_changed_notification,
    send_support_group_creation_notification,
    send_external_join_confirmation,
    invite_to_group,
    create_group_creation_confirmation_activity,
    send_membership_transfer_notifications,
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
from agir.lib.tasks import geocode_support_group
from agir.people.models import Person

__all__ = [
    "SupportGroupForm",
    "AddReferentForm",
    "AddManagerForm",
    "InvitationForm",
    "GroupGeocodingForm",
    "SearchGroupForm",
    "TransferGroupMembersForm",
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


class MembershipChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.person)


class MembershipMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return str(obj.person)


class SupportGroupChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj)


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

        referent_candidates = self.fields["referent"].queryset.filter(
            supportgroup=support_group
        )

        if support_group.is_2022:
            # Filter out group members that are already referent or manager of another nsp group
            referent_candidates = referent_candidates.annotate(
                already_referent=Exists(
                    SupportGroup.objects.active().filter(
                        type__in=[id for id, _ in SupportGroup.TYPE_NSP_CHOICES],
                        memberships__person_id=OuterRef("person_id"),
                        memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
                    )
                )
            ).filter(already_referent=False)

        self.fields["referent"].queryset = referent_candidates

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

        manager_candidates = self.fields["manager"].queryset.filter(
            supportgroup=support_group
        )

        if support_group.is_2022:
            # Filter out group members that are already referent or manager of another nsp group
            manager_candidates = manager_candidates.annotate(
                already_manager=Exists(
                    SupportGroup.objects.active().filter(
                        type__in=[id for id, _ in SupportGroup.TYPE_NSP_CHOICES],
                        memberships__person_id=OuterRef("person_id"),
                        memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
                    )
                )
            ).filter(already_manager=False)

        self.fields["manager"].queryset = manager_candidates
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

    def __init__(self, person, supportgroup, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.supportgroup = supportgroup

        supportgroup_members = Membership.objects.filter(
            supportgroup=supportgroup
        ).exclude(person=person)

        self.fields["members"].queryset = self.fields[
            "members"
        ].queryset = supportgroup_members

        base_query = {"exclude": supportgroup.pk}

        if supportgroup.is_2022:
            base_query["is_2022"] = 1
            self.fields[
                "target_group"
            ].help_text = "Le nouveau groupe doit avoir déjà été créé par quelqu'un d'autre pour pouvoir y transférer une partie de vos membres."
        else:
            base_query["is_insoumise"] = 1

        self.fields["target_group"].widget = RemoteSelectizeWidget(
            api_url=reverse_lazy("api_search_group"),
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
            transfer_operation = TranferOperation.objects.create(
                previous_group=self.supportgroup, new_group=target_group
            )
            transfer_operation.members.add(*(m.person for m in memberships))

            for membership in memberships:
                Membership.objects.update_or_create(
                    person=membership.person, supportgroup=target_group
                )
                membership.delete()

        send_membership_transfer_notifications.delay(
            self.supportgroup.pk,
            target_group.pk,
            [membership.person.pk for membership in memberships],
        )

        return {
            "target_group": target_group,
            "transferred_memberships": memberships,
        }
