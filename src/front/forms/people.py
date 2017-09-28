from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions

from ..form_components import *
from ..form_mixins import TagMixin, LocationFormMixin

from people.models import Person, PersonEmail, PersonTag
from people.tags import skills_tags, action_tags

__all__ = [
    'BaseSubscriptionForm', 'SimpleSubscriptionForm', 'OverseasSubscriptionForm', 'EmailFormSet', 'ProfileForm',
    'VolunteerForm', "MessagePreferencesForm",
]


class BaseSubscriptionForm(forms.ModelForm):
    email = forms.EmailField(
        label='Adresse email',
        required=True,
        error_messages={
            'required': _("Vous devez saisir votre adresse email"),
            'unique': _("Cette adresse email est déjà utilisée")
        }
    )

    def clean_email(self):
        """Ensures that the email address is not already in use"""
        email = self.cleaned_data['email']

        if PersonEmail.objects.filter(address=email).exists():
            raise forms.ValidationError(self.fields['email'].error_messages['unique'], code="unique")

        return email

    def _save_m2m(self):
        """Save the email

        _save_m2m is called when the ModelForm instance is saved, whether it is made through
        the form itself using `form.save(commit=True)` or later, using `instance = form.save(commit=False)`
        and calling `instance.save()`later.
        """
        super()._save_m2m()
        PersonEmail.objects.create(address=self.cleaned_data['email'], person=self.instance)

    class Meta:
        abstract = True


class SimpleSubscriptionForm(BaseSubscriptionForm):
    def __init__(self, *args, **kwargs):
        super(SimpleSubscriptionForm, self).__init__(*args, **kwargs)

        self.fields['location_zip'].required = True
        self.fields['location_zip'].help_text = None

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            FormGroup(
                Field("email", placeholder=self.fields['email'].label, css_class='input-lg'),
                css_class="col-sm-12"
            ),
            FormGroup(
                Div(
                    Field("location_zip", placeholder=self.fields['location_zip'].label, css_class='input-lg'),
                    css_class="col-sm-6"
                ),
                Div(
                    Submit('submit', 'Appuyer', css_class="btn-block btn-lg"),
                    css_class="col-sm-6"
                )
            )
        )

    class Meta:
        model = Person
        fields = ('email', 'location_zip')


class OverseasSubscriptionForm(LocationFormMixin, BaseSubscriptionForm):
    def __init__(self, *args, **kwargs):
        super(OverseasSubscriptionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Appuyer'))

        self.helper.layout = Layout(
            Row(
                FullCol('email'),
            ),
            Row(
                FullCol(
                    Field('location_address1', placeholder='Ligne 1*'),
                    Field('location_address2', placeholder='Ligne 2'),
                )

            ),
            Row(
                Div('location_zip', css_class='col-md-4'),
                Div('location_city', css_class='col-md-8'),
            ),
            Row(
                FullCol('location_country'),
            )
        )

    class Meta:
        model = Person
        fields = (
            'email', 'location_address1', 'location_address2', 'location_zip', 'location_city', 'location_country'
        )


EmailFormSet = forms.inlineformset_factory(
    parent_model=Person,
    model=PersonEmail,
    fields=('address',),
    can_delete=True,
    can_order=True,
    min_num=1,
)


class ProfileForm(TagMixin, forms.ModelForm):
    tags = skills_tags
    tag_model_class = PersonTag
    meta_fields = ['occupation', 'associations', 'unions', 'party', 'party_responsibility', 'other']

    occupation = forms.CharField(max_length=200, label=_("Métier"), required=False)
    associations = forms.CharField(max_length=200, label=_("Engagements associatifs"), required=False)
    unions = forms.CharField(max_length=200, label=_("Engagements syndicaux"), required=False)
    party = forms.CharField(max_length=60, label=_("Parti politique"), required=False)
    party_responsibility = forms.CharField(max_length=100, label=False, required=False)
    other = forms.CharField(max_length=200, label=_("Autres engagements"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in self.meta_fields:
            self.fields[f].initial = self.instance.meta.get(f)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Enregistrer mes informations'))

        self.fields['location_address1'].label = _("Adresse")
        self.fields['location_address2'].label = False

        self.helper.layout = Layout(
            Row(
                HalfCol(  # contact part
                    Row(
                        HalfCol('first_name'),
                        HalfCol('last_name')
                    ),
                    Row(
                        HalfCol('gender'),
                        HalfCol('date_of_birth')
                    ),
                    Row(
                        FullCol(
                            Field('location_address1', placeholder=_('1ère ligne')),
                            Field('location_address2', placeholder=_('2ème ligne'))
                        )
                    ),
                    Row(
                        HalfCol('location_zip'),
                        HalfCol('location_city')
                    ),
                    Row(
                        FullCol('location_country')
                    ),
                    Row(
                        HalfCol('contact_phone'),
                        HalfCol('occupation')
                    ),
                    Row(
                        HalfCol('associations'),
                        HalfCol('unions')
                    ),
                    Row(
                        HalfCol(
                            Field('party', placeholder='Nom du parti'),
                            Field('party_responsibility', placeholder='Responsabilité')),
                        HalfCol('other')
                    )
                ),
                HalfCol(
                    HTML('<label>Savoir-faire</label>'),
                    *(tag for tag, desc in skills_tags)
                )
            )
        )

    def clean(self):
        """Handles meta fields"""
        cleaned_data = super().clean()

        meta_update = {f: cleaned_data.pop(f) for f in self.meta_fields}
        self.instance.meta.update(meta_update)

        return cleaned_data

    class Meta:
        model = Person
        fields = (
            'first_name', 'last_name',
            'location_address1', 'location_address2', 'location_city', 'location_zip', 'location_country',
            'contact_phone'
        )


class VolunteerForm(TagMixin, forms.ModelForm):
    tags = [
        (tag, format_html('<strong>{}</strong><br><small><em>{}</em></small>', title, description))
        for _, tags in action_tags.items() for tag, title, description in tags]
    tag_model_class = PersonTag

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', _("M'enregistrer comme volontaire")))

        self.helper.layout = Layout(
            Row(
                HalfCol(
                    HTML(format_html("<h4>{}</h4>", "Agir près de chez vous")),
                    *(tag for tag, title, desc in action_tags['nearby'])
                ),
                HalfCol(
                    HTML(format_html("<h4>{}</h4>", "Agir sur internet")),
                    *(tag for tag, title, desc in action_tags['internet'])
                ),
            ),
            Row(
                HalfCol(
                    'contact_phone'
                )
            )
        )

    class Meta:
        model = Person
        fields = (
            'contact_phone',
        )


class MessagePreferencesForm(forms.ModelForm):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

        self.no_mail = data is not None and 'no_mail' in data

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            'subscribed',
            'group_notifications',
            'event_notifications',
            FormActions(
                Submit('submit', 'Sauvegarder mes préférences'),
                Submit('no_mail', 'Ne plus recevoir de mails du tout', css_class='btn-danger')
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        if self.no_mail:
            cleaned_data = {k: False for k in cleaned_data}

        return cleaned_data

    class Meta:
        model = Person
        fields = ['subscribed', 'group_notifications', 'event_notifications']
