from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper

from ..form_components import *
from ..form_mixins import LocationFormMixin

from groups.models import SupportGroup

__all__ = ['SupportGroupForm', 'AddReferentForm', 'AddManagerForm']


class SupportGroupForm(LocationFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SupportGroupForm, self).__init__(*args, **kwargs)

        self.fields['location_name'].required = True

        self.fields['location_address1'].label = _('Adresse')
        self.fields['location_address1'].required = True

        self.fields['location_address2'].label = False

        self.fields['location_city'].required = True

        self.fields['location_country'].required = True

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sauvegarder et publier'))

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
            Div(HTML(
                "<strong>"
                "Cliquez sur sauvegarder et publier pour valider les changements effectués ci-dessous."
                "</strong>"
            ))
        )

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
        person = obj.person
        if person.first_name and person.last_name:
            return "{} {} <{}>".format(person.first_name, person.last_name, person.email)
        else:
            return person.email


class AddReferentForm(forms.Form):
    form = forms.CharField(initial="add_referent_form", widget=forms.HiddenInput())

    def __init__(self, support_group, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['referent'] = MembershipChoiceField(
            queryset=support_group.memberships.filter(is_referent=False),
            label=_('Nouveau référent')
        )

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Ajouter comme second référent')))

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
