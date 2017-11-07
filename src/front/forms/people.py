from crispy_forms.layout import Fieldset
from django import forms
from django.contrib.auth.models import BaseUserManager
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions

from ..form_components import *
from ..form_mixins import TagMixin, LocationFormMixin

from people.models import Person, PersonEmail, PersonTag, PersonFormSubmission
from people.tags import skills_tags, action_tags
from people.tasks import send_unsubscribe_email, send_welcome_mail

__all__ = [
    'BaseSubscriptionForm', 'SimpleSubscriptionForm', 'OverseasSubscriptionForm', 'EmailFormSet', 'ProfileForm',
    'VolunteerForm', "MessagePreferencesForm", 'UnsubscribeForm', 'AddEmailForm', 'get_people_form_class'
]

class ContactPhoneNumberMixin():
    """Solves a bug in phonenumbers_fields when field is missing from POSTed data

    """

    def clean_contact_phone(self):
        contact_phone = self.cleaned_data.get('contact_phone')

        if contact_phone is None:
            contact_phone = ''

        return contact_phone


class UnsubscribeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Me désabonner'))

    email = forms.EmailField(
        label='Adresse email',
        required=True,
        error_messages={
            'required': _("Vous devez saisir votre adresse email")
        }
    )

    def unsubscribe(self):
        email = self.cleaned_data['email']
        try:
            person = Person.objects.get(email=email)
            send_unsubscribe_email.delay(person.id)
            person.group_notifications = False
            person.event_notifications = False
            person.subscribed = False
            person.save()
        except(Person.DoesNotExist):
            pass


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
        send_welcome_mail.delay(self.instance.pk)

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


class ProfileForm(ContactPhoneNumberMixin, TagMixin, forms.ModelForm):
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
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'location_address1', 'location_address2', 'location_city', 'location_zip', 'location_country',
            'contact_phone'
        )


class VolunteerForm(ContactPhoneNumberMixin, TagMixin, forms.ModelForm):
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

        self.fields['gender'].help_text = _("La participation aux tirages au sort étant paritaire, merci d'indiquer"
                                            " votre genre si vous souhaitez être tirés au sort.")

        emails = self.instance.emails.all()
        self.several_mails = len(emails) > 1

        fields = []

        block_template = """
            <label class="control-label">{label}</label>
            <div class="controls">
              <div>{value}</div>
              <p class="help-block">{help_text}</p>
            </div>
        """

        email_management_link = HTML(block_template.format(
            label=_("Gérez vos adresses emails"),
            value=format_html(
                '<a href="{}" class="btn btn-default">{}</a>',
                reverse('email_management'),
                _("Accéder au formulaire de gestion de vos emails"),
            ),
            help_text=_("Ce formulaire vous permet d'ajouter de nouvelles adresses ou de supprimer les existantes"),
        ))

        email_fieldset_name = _("Mes adresses emails")
        email_label = _("Email de contact")
        email_help_text = _(
            "L'adresse que nous utilisons pour vous envoyer les lettres d'informations et les notifications."
        )

        if self.several_mails:
            self.fields['primary_email'] = forms.ModelChoiceField(
                queryset=emails,
                required=True,
                label=email_label,
                initial=emails[0],
                help_text=email_help_text,
            )
            fields.append(
                Fieldset(
                    email_fieldset_name,
                    Row(
                        HalfCol('primary_email'),
                        HalfCol(email_management_link)
                    )
                )
            )
        else:
            fields.append(Fieldset(
                email_fieldset_name,
                Row(
                    HalfCol(
                        HTML(block_template.format(
                            label=email_label,
                            value=emails[0].address,
                            help_text=email_help_text
                        ))
                    ),
                    HalfCol(email_management_link)
                )
            ))

        fields.extend([
            Fieldset(
                _("Préférences d'emails"),
                'subscribed',
                'group_notifications',
                'event_notifications',
            ),
            Fieldset(
                _("Ma participation"),
                Row(
                    HalfCol('draw_participation'),
                    HalfCol('gender'),
                )
            ),
            FormActions(
                Submit('submit', 'Sauvegarder mes préférences'),
                Submit('no_mail', 'Ne plus recevoir de mails du tout', css_class='btn-danger')
            )
        ])

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(*fields)

    def clean(self):
        cleaned_data = super().clean()

        if self.no_mail:
            for k, v in cleaned_data.items():
                if not isinstance(v, bool): continue
                cleaned_data[k] = False

        if cleaned_data['draw_participation'] and not cleaned_data['gender']:
            self.add_error(
                'gender',
                forms.ValidationError(
                    _("Votre genre est obligatoire pour pouvoir organiser un tirage au sort paritaire"))
            )

        return cleaned_data

    def _save_m2m(self):
        """Reorder addresses so that the selected one is number one"""
        if 'primary_email' in self.cleaned_data:
            self.instance.set_primary_email(self.cleaned_data['primary_email'])

    class Meta:
        model = Person
        fields = ['subscribed', 'group_notifications', 'event_notifications', 'draw_participation', 'gender']


class AddEmailForm(forms.ModelForm):
    def __init__(self, person, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance.person = person
        self.fields['address'].label = _("Nouvelle adresse")
        self.fields['address'].help_text = _("Utiliser ce champ pour ajouter une adresse supplémentaire que vous pouvez"
                                             " utiliser pour vous connecter.")
        self.fields['address'].error_messages['unique'] = _("Cette adresse est déjà rattaché à un autre compte.")

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Ajouter'))

    def clean_address(self):
        """Normalize the domain part the domain part of the email address"""
        address = self.cleaned_data['address']
        return BaseUserManager.normalize_email(address)

    class Meta:
        model = PersonEmail
        fields = ("address",)


class PersonTagChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description


class BasePersonForm(forms.ModelForm):
    person_form_instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parts = []

        self.tag_queryset = self.person_form_instance.tags.all()

        if len(self.tag_queryset) > 1:
            self.fields['tag'] = PersonTagChoiceField(
                queryset=self.tag_queryset,
                required=True,
                label=self.person_form_instance.main_question
            )
            parts.append(Fieldset(
                _('Ma situation'),
                Row(FullCol('tag'))
            ))
        elif len(self.tag_queryset) == 1:
            self.tag = self.tag_queryset[0]

        opts = self._meta
        if opts.fields:
            for f in opts.fields:
                self.fields[f].required = True

            parts.append(
                Fieldset(
                    _('Mes informations personnelles'),
                    *[Row(FullCol(f)) for f in opts.fields]
                )
            )

        if self.person_form_instance.additional_fields:
            for field in self.person_form_instance.additional_fields:
                kwargs = {}
                if 'attrs' in field:
                    kwargs.update(field['attrs'])
                if 'widget' in field:
                    kwargs['widget'] = getattr(forms, field['widget'])

                self.fields[field['id']] = getattr(forms, field['class'])(
                    **kwargs
                )

            parts.append(
                Fieldset(
                    _('Les détails'),
                    *[Row(FullCol(f['id'])) for f in self.person_form_instance.additional_fields]
                )
            )

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Envoyer'))

        self.helper.layout = Layout(*parts)

    def _save_m2m(self):
        if 'tag' in self.cleaned_data:
            self.instance.tags.add(self.cleaned_data['tag'])
        elif hasattr(self, 'tag'):
            self.instance.tags.add(self.tag)

        if self.person_form_instance.additional_fields:
            PersonFormSubmission.objects.create(
                form=self.person_form_instance,
                data={
                    f['id']: self.cleaned_data[f['id']] for f in self.person_form_instance.additional_fields
                }
            )

    class Meta:
        model = Person
        fields = []


def get_people_form_class(person_form_instance):
    form_class = forms.modelform_factory(Person, fields=person_form_instance.personal_information, form=BasePersonForm)
    form_class.person_form_instance = person_form_instance

    return form_class
