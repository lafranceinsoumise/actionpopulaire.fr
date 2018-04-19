from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import keep_lazy_text
from django.utils.html import mark_safe
from django.utils.formats import number_format
from django.utils.text import format_lazy

from django_countries.fields import CountryField

from crispy_forms import layout
from crispy_forms.helper import FormHelper

from front.form_mixins import MetaFieldsMixin
from people.models import Person, PersonEmail

from .form_fields import AmountWidget

__all__ = ('DonationForm', 'DonatorForm')


class DonationForm(forms.Form):
    amount = forms.DecimalField(
        label='Montant du don',
        max_value=settings.DONATION_MAXIMUM,
        min_value=settings.DONATION_MINIMUM,
        decimal_places=2,
        required=True,
        error_messages={
            'invalid': _("Indiquez le montant à donner."),
            'min_value': format_lazy(
                _("Il n'est pas possible de donner moins que {min} €."),
                min=settings.DONATION_MINIMUM
            ),
            'max_value': format_lazy(
                _("Les dons de plus de {max} € ne peuvent être faits par carte bleue."),
                max=settings.DONATION_MAXIMUM
            )
        },
        widget=AmountWidget()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(layout.Submit('valider', 'Je donne !'))


class DonatorForm(MetaFieldsMixin, forms.ModelForm):
    meta_fields = ['nationality']

    email = forms.EmailField(
        label=_('Votre adresse email'),
        required=True,
        help_text=_(
            "Si vous êtes déjà inscrit⋅e sur la plateforme, utilisez l'adresse avec laquelle vous êtes inscrit⋅e"
        )
    )

    amount = forms.IntegerField(
        max_value=settings.DONATION_MAXIMUM*100,
        min_value=settings.DONATION_MINIMUM*100,
        required=True,
        widget=forms.HiddenInput
    )

    declaration = forms.BooleanField(
        required=True,
        label=_("Je certifie sur l'honneur être une personne physique et que le réglement de mon don ne provient pas"
                " d'une personne morale (association, société, société civile...) mais de mon compte bancaire"
                " personnel."),
        help_text=keep_lazy_text(mark_safe)(
            "Un reçu, édité par la <abbr title=\"Commission Nationale des comptes de campagne et des financements"
            " politiques\">CNCCFP</abbr>, me sera adressé, et me permettra de déduire cette somme de mes impôts"
            " dans les limites fixées par la loi.")
    )

    nationality = CountryField(blank=False, blank_label=_("Indiquez le pays dont vous êtes citoyen")).formfield(
        label=_("Nationalité"),
        help_text=_('Indiquez France, si vous êtes de double nationalité, dont française.')
    )

    fiscal_resident = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'disabled': True}),
        label=_("Je certifie être domicilié⋅e fiscalement en France")
    )

    def __init__(self, amount, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['amount'].initial = amount

        self.adding = self.instance._state.adding

        if not self.adding:
            del self.fields['email']

        # we remove the subscribed field for people who are already subscribed
        if not self.adding and self.instance.subscribed:
            del self.fields['subscribed']
        else:
            # we want the subscribed field to be prechecked only for new email subscribers
            self.fields['subscribed'].initial = self.adding

        fields = ['amount']

        if 'email' in self.fields:
            fields.append('email')

        fields.extend(['declaration', 'nationality', 'fiscal_resident'])
        fields.extend(['first_name', 'last_name'])
        fields.extend(['location_address1', 'location_address2', 'location_zip', 'location_city', 'location_country'])
        fields.append('contact_phone')

        self.helper = FormHelper()
        self.helper.add_input(layout.Submit('valider', f'Je donne {number_format(amount / 100, 2)} €'))
        self.helper.layout = layout.Layout(
            *fields
        )

    def clean(self):
        cleaned_data = super().clean()

        nationality, fiscal_resident = cleaned_data.get('nationality'), cleaned_data.get('fiscal_resident')

        if nationality != 'FR' and not fiscal_resident:
            self.add_error('fiscal_resident', forms.ValidationError(
                _('Les personnes non-françaises doivent être fiscalement domiciliées en France.'),
                code='not_fiscal_resident'
            ))

        return cleaned_data

    def _save_m2m(self):
        if self.adding:
            PersonEmail.objects.create_email(
                address=self.cleaned_data['email'],
                person=self.instance,
            )

    class Meta:
        model = Person
        fields = (
            'first_name', 'last_name', 'location_address1', 'location_address2', 'location_zip',
            'location_country', 'contact_phone', 'subscribed'
        )
