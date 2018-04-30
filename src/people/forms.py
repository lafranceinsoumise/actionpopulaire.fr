from django import forms
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from phonenumber_field.formfields import PhoneNumberField

from .form_mixins import MetaFieldsMixin
from .models import Person, PersonFormSubmission
from lib.form_components import *


all_person_field_names = [field.name for field in Person._meta.get_fields()]


class PersonTagChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description


class BasePersonForm(MetaFieldsMixin, forms.ModelForm):
    person_form_instance = None

    def get_meta_fields(self):
        return [field['id']
                for fieldset in self.person_form_instance.custom_fields
                for field in fieldset['fields']
                if field.get('person_field') and field['id'] not in all_person_field_names]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parts = []

        self.tag_queryset = self.person_form_instance.tags.all()

        if len(self.tag_queryset) > 1:
            self.fields['tag'] = PersonTagChoiceField(
                queryset=self.tag_queryset,
                to_field_name='label',
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

        if self.person_form_instance.custom_fields:
            for fieldset in self.person_form_instance.custom_fields:
                for field in fieldset['fields']:
                    if not field.get('person_field') or field['id'] not in all_person_field_names:
                        kwargs = {'required': True}
                        if field['type'] in ['short_text', 'long_text']:
                            klass = forms.CharField
                            if 'max_length' in field:
                                kwargs['max_length'] = field['max_length']
                            if field['type'] == 'long_text':
                                kwargs['widget'] = forms.Textarea()
                        elif field['type'] == 'choice':
                            klass = forms.ChoiceField
                            default_label = "----" if kwargs['required'] else _("Non applicable / ne souhaite pas répondre")
                            kwargs['choices'] = [('', default_label)] + field['choices']
                        elif field['type'] == 'multiple_choice':
                            klass = forms.MultipleChoiceField
                            kwargs['choices'] = field['choices']
                            kwargs['widget'] = forms.CheckboxSelectMultiple()
                            # by default multiple choice field is not required
                            kwargs['required'] = False
                        elif field['type'] == 'email_address':
                            klass = forms.EmailField
                        elif field['type'] == 'phone_number':
                            klass = PhoneNumberField
                        else:
                            klass = forms.BooleanField
                            # by default boolean field should be false or one is forced to tick the checkbox to proceed
                            kwargs['required'] = False

                        self.fields[field['id']] = klass(**kwargs)
                    else:
                        # by default meta fields are required
                        self.fields[field['id']].required = True

                        if field['id'] == 'date_of_birth':
                            self.fields[field['id']].help_text = 'Format JJ/MM/AAAA'

                    field_object = self.fields[field['id']]

                    for prop in ['label', 'help_text', 'required']:
                        if prop in field:
                            setattr(field_object, prop, field[prop])

                parts.append(
                    Fieldset(fieldset['title'], *(Row(FullCol(field['id'])) for field in fieldset['fields']))
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

        self.submission = PersonFormSubmission.objects.create(
            person=self.instance,
            form=self.person_form_instance,
            data={
                field['id']: str(self.cleaned_data[field['id']])
                for fieldset in self.person_form_instance.custom_fields
                for field in fieldset['fields']
            }
        )

    class Meta:
        model = Person
        fields = []


def get_people_form_class(person_form_instance):
    form_person_fields = [field['id'] for fieldset in person_form_instance.custom_fields for field in fieldset['fields']
                          if field.get('person_field') and field['id'] in all_person_field_names]
    form_class = forms.modelform_factory(Person, fields=form_person_fields, form=BasePersonForm)
    form_class.person_form_instance = person_form_instance

    return form_class
