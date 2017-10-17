from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper

from ..form_components import *
from ..form_mixins import LocationFormMixin, ContactFormMixin

from groups.models import SupportGroup, Membership
from groups.tasks import send_support_group_changed_notification, send_support_group_creation_notification
from lib.tasks import geocode_support_group

__all__ = ['SupportGroupForm', 'AddReferentForm', 'AddManagerForm']


class SupportGroupForm(LocationFormMixin, ContactFormMixin, forms.ModelForm):
    CHANGES = {
        'name': "information",
        'contact_name': "contact",
        'contact_email': "contact",
        'contact_phone': "contact",
        'contact_hide_phone': "contact",
        'location_name': "location",
        'location_address1': "location",
        'location_address2': "location",
        'location_city': "location",
        'location_zip': "location",
        'location_country': "location",
        'description': "information"
    }

    def __init__(self, *args, person, **kwargs):
        super(SupportGroupForm, self).__init__(*args, **kwargs)

        self.person = person
        self.is_creation = self.instance._state.adding

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sauvegarder et publier'))

        if not self.is_creation:
            self.fields['notify'] = forms.BooleanField(
                required=False,
                initial=False,
                label=_("Signalez ces changements aux membres du groupe"),
                help_text=_("Un email sera envoyé à la validation de ce formulaire. Merci de ne pas abuser de cette"
                            " fonctionnalité.")
            )
            notify_field = [Row(
                FullCol('notify')
            )]
        else:
            notify_field = []

        self.helper.layout = Layout(
            Row(
                FullCol('name'),
            ),
            Section(
                _('Informations de contact'),
                Row(
                    Div('contact_name', css_class='col-md-12')
                ),
                Row(
                    HalfCol('contact_email', css_class='col-md-6'),
                    HalfCol('contact_phone', 'contact_hide_phone', css_class='col-md-6')
                )
            ),
            Section(
                _('Lieu'),
                Row(
                    HTML(
                        "<p><b>Merci d'indiquer une adresse précise avec numéro de rue, sans quoi le groupe"
                        " n'apparaîtra pas sur la carte.</b>"
                        " Si les réunions se déroulent chez vous et que vous ne souhaitez pas rendre cette adresse"
                        " publique, vous pouvez indiquer un endroit à proximité, comme un café, ou votre mairie."),
                    css_class='col-xs-12'
                ),
                Row(
                    FullCol('location_name'),
                ),
                Row(
                    FullCol(
                        Field('location_address1', placeholder=_('1ère ligne')),
                        Field('location_address2', placeholder=_('2ème ligne'))
                    )
                ),
                Row(
                    Div('location_zip', css_class='col-md-4'),
                    Div('location_city', css_class='col-md-8'),
                ),
                Row(
                    FullCol('location_country'),
                )
            ),
            Row(
                FullCol('description'),
            ),
            *notify_field
        )

    def save(self, commit=True):
        res = super().save(commit=commit)

        if commit:
            self.schedule_tasks()

        return res

    def _save_m2m(self):
        if self.is_creation:
            self.membership = Membership.objects.create(
                person=self.person, supportgroup=self.instance,
                is_referent=True, is_manager=True,
            )

    def schedule_tasks(self):
        # create set so that values are unique, but turns to list because set are not JSON-serializable
        changes = list({self.CHANGES[field] for field in self.changed_data if field in self.CHANGES})
        address_changed = any(f in self.instance.GEOCODING_FIELDS for f in self.changed_data)

        # if it's a new group creation, send the confirmation notification and geolocate it
        if self.is_creation:
            # membership attribute created by _save_m2m
            send_support_group_creation_notification.delay(self.membership.pk)
            geocode_support_group.delay(self.instance.pk)
        else:
            # send changes notification if the notify checkbox was checked
            if changes and self.cleaned_data.get('notify'):
                send_support_group_changed_notification.delay(self.instance.pk, changes)
            # also geocode again if location has changed
            if address_changed and self.instance.should_relocate_when_address_changed():
                geocode_support_group.delay(self.instance.pk)

    class Meta:
        model = SupportGroup
        fields = (
            'name',
            'contact_name', 'contact_email', 'contact_phone', 'contact_hide_phone',
            'location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
            'location_country',
            'description'
        )


class MembershipChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.person)


class AddReferentForm(forms.Form):
    form = forms.CharField(initial="add_referent_form", widget=forms.HiddenInput())

    def __init__(self, support_group, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['referent'] = MembershipChoiceField(
            queryset=support_group.memberships.filter(is_referent=False),
            label=_('Second animateur')
        )

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Signaler comme second animateur')))

    def save(self, commit=True):
        membership = self.cleaned_data['referent']

        membership.is_referent = True
        membership.is_manager = True

        if commit:
            membership.save()

        return membership


class AddManagerForm(forms.Form):
    form = forms.CharField(initial="add_manager_form", widget=forms.HiddenInput())

    def __init__(self, support_group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_group = support_group

        self.fields['manager'] = MembershipChoiceField(
            queryset=support_group.memberships.filter(is_manager=False), label=False
        )

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Ajouter comme membre gestionnaire')))

    def save(self, commit=True):
        membership = self.cleaned_data['manager']

        membership.is_manager = True

        if commit:
            membership.save()

        return membership
