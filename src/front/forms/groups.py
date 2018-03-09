from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from crispy_forms.helper import FormHelper

from ..form_components import *
from ..form_mixins import LocationFormMixin, ContactFormMixin, GeocodingBaseForm, SearchByZipCodeFormBase

from groups.models import SupportGroup, Membership, SupportGroupSubtype
from groups.tasks import send_support_group_changed_notification, send_support_group_creation_notification
from lib.tasks import geocode_support_group

__all__ = ['SupportGroupForm', 'AddReferentForm', 'AddManagerForm', 'GroupGeocodingForm', 'SearchGroupForm']


class SupportGroupForm(LocationFormMixin, ContactFormMixin, forms.ModelForm):
    geocoding_task = geocode_support_group

    CHANGES = {
        'name': "information",
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

    subtypes = forms.ModelMultipleChoiceField(
        queryset=SupportGroupSubtype.objects.filter(privileged_only=False),
        to_field_name='label',
    )

    def __init__(self, *args, person, **kwargs):
        super(SupportGroupForm, self).__init__(*args, **kwargs)

        self.person = person
        self.is_creation = self.instance._state.adding

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sauvegarder et publier'))

        # do not allow random organizers to modify HTML
        if self.instance.allow_html:
            del self.fields['description']
            description_field = []

        if not self.is_creation:
            self.fields['notify'] = forms.BooleanField(
                required=False,
                initial=False,
                label=_("Signalez ces changements aux membres du groupe"),
                help_text=_("Un email sera envoyé à la validation de ce formulaire. Merci de ne pas abuser de cette"
                            " fonctionnalité.")
            )
            del self.fields['type']
            del self.fields['subtypes']
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
        super()._save_m2m()
        if self.is_creation:
            self.membership = Membership.objects.create(
                person=self.person, supportgroup=self.instance,
                is_referent=True, is_manager=True,
            )

    def schedule_tasks(self):
        super().schedule_tasks()

        # create set so that values are unique, but turns to list because set are not JSON-serializable
        changes = list({self.CHANGES[field] for field in self.changed_data if field in self.CHANGES})

        # if it's a new group creation, send the confirmation notification and geolocate it
        if self.is_creation:
            # membership attribute created by _save_m2m
            send_support_group_creation_notification.delay(self.membership.pk)
        else:
            # send changes notification if the notify checkbox was checked
            if changes and self.cleaned_data.get('notify'):
                send_support_group_changed_notification.delay(self.instance.pk, changes)

    class Meta:
        model = SupportGroup
        fields = (
            'name', 'type', 'subtypes',
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


class GroupGeocodingForm(GeocodingBaseForm):
    geocoding_task = geocode_support_group
    messages = {
        'use_geocoding': _("La localisation de votre groupe sur la carte va être réinitialisée à partir de son adresse."
                           " Patientez quelques minutes pour voir la nouvelle localisation apparaître."),
        'coordinates_updated': _("La localisation de votre groupe a été correctement mise à jour. Patientez quelques"
                                 " minutes pour la voir apparaître sur la carte.")
    }

    class Meta:
        model = SupportGroup
        fields = ('coordinates',)


class SearchGroupForm(SearchByZipCodeFormBase):
    pass
