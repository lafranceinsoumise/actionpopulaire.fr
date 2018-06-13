from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from phonenumber_field.formfields import PhoneNumberField

from agir.lib.form_components import *
from ..form_mixins import MetaFieldsMixin

from ..models import Person, PersonFormSubmission


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
                for field_descriptor in fieldset['fields']:
                    is_actual_model_field = field_descriptor.get('person_field', False) and field_descriptor['id'] in all_person_field_names

                    if is_actual_model_field:
                        # by default person fields are required
                        self.fields[field_descriptor['id']].required = True

                        if field_descriptor['id'] == 'date_of_birth':
                            self.fields[field_descriptor['id']].help_text = _('Format JJ/MM/AAAA')
                    else:
                        self.fields[field_descriptor['id']] = get_form_field(field_descriptor)

                    field_object = self.fields[field_descriptor['id']]

                    for prop in ['label', 'help_text', 'required']:
                        if prop in field_descriptor:
                            setattr(field_object, prop, field_descriptor[prop])

                parts.append(
                    Fieldset(fieldset['title'], *(Row(FullCol(field['id'])) for field in fieldset['fields']))
                )

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Envoyer'))

        self.helper.layout = Layout(*parts)

    def save_submission(self, person):
        if person is None:
            person = self.instance

        self.submission = PersonFormSubmission.objects.create(
            person=person,
            form=self.person_form_instance,
            data={
                field['id']: str(self.cleaned_data[field['id']])
                for fieldset in self.person_form_instance.custom_fields
                for field in fieldset['fields']
            }
        )

        return self.submission

    def _save_m2m(self):
        if 'tag' in self.cleaned_data:
            self.instance.tags.add(self.cleaned_data['tag'])
        elif hasattr(self, 'tag'):
            self.instance.tags.add(self.tag)

        if not hasattr(self, 'submission'):
            self.save_submission(self.instance)

    class Meta:
        model = Person
        fields = []


def get_form_field(field_descriptor):
    kwargs = {'required': True}
    if field_descriptor['type'] in ['short_text', 'long_text']:
        klass = forms.CharField
        if 'max_length' in field_descriptor:
            kwargs['max_length'] = field_descriptor['max_length']
        if field_descriptor['type'] == 'long_text':
            kwargs['widget'] = forms.Textarea()
    elif field_descriptor['type'] == 'choice':
        klass = forms.ChoiceField
        default_label = "----" if kwargs['required'] else _("Non applicable / ne souhaite pas répondre")
        kwargs['choices'] = [('', default_label)] + field_descriptor['choices']
    elif field_descriptor['type'] == 'multiple_choice':
        klass = forms.MultipleChoiceField
        kwargs['choices'] = field_descriptor['choices']
        kwargs['widget'] = forms.CheckboxSelectMultiple()
        # by default multiple choice field is not required
        kwargs['required'] = False
    elif field_descriptor['type'] == 'email_address':
        klass = forms.EmailField
    elif field_descriptor['type'] == 'phone_number':
        klass = PhoneNumberField
    else:
        klass = forms.BooleanField
        # by default boolean field should be false or one is forced to tick the checkbox to proceed
        kwargs['required'] = False

    return klass(**kwargs)


def get_people_form_class(person_form_instance, base_form=BasePersonForm):
    """Returns the form class for the specific person_form_instance

    :param person_form_instance: the person_form model object for which the form class must be generated
    :param base_form: an optional base form to use instead of the default BasePersonForm
    :return: a form class that can be used to generate a form for the person_form_instance
    """
    # the list of 'person_fields' that will also be saved on the person model when saving the form
    form_person_fields = [field['id'] for fieldset in person_form_instance.custom_fields for field in fieldset['fields']
                          if field.get('person_field') and field['id'] in all_person_field_names]

    form_class = forms.modelform_factory(Person, fields=form_person_fields, form=base_form)
    form_class.person_form_instance = person_form_instance

    return form_class


def get_form_field_labels(form):
    field_dicts = form.fields_dict
    field_information = {}

    person_fields = {f.name: f for f in Person._meta.get_fields()}

    for id, field in field_dicts.items():
        if field.get('person_field') and id in person_fields:
            field_information[id] = field_dicts[id].get(
                'label',
                getattr(person_fields[id], 'verbose_name', person_fields[id].name)
            )
        else:
            field_information[id] = field_dicts[id]['label']

    return field_information


def get_formatted_submission(submission):
    data = submission.data
    field_dicts = submission.form.fields_dict
    labels = get_form_field_labels(submission.form)
    choice_fields = {id: dict(f['choices']) for id, f in field_dicts.items() if f.get('type') in ['choice', 'multiple_choice']}

    res = []

    for id, field in field_dicts.items():
        if id in data:
            if id in choice_fields:
                res.append({'label': labels[id], 'value': choice_fields[id].get(data[id], data[id])})
            else:
                res.append({'label': labels[id], 'value': data[id]})

    missing_fields = set(data) - set(field_dicts)

    for id in sorted(missing_fields):
        res.append({'label': id, 'value': data[id]})

    return res


def validate_custom_fields(custom_fields):
    if not isinstance(custom_fields, list):
        raise ValidationError('La valeur doit être une liste')
    for fieldset in custom_fields:
        if not (fieldset.get('title') and isinstance(fieldset['fields'], list)):
            raise ValidationError('Les sections doivent avoir un "title" et une liste "fields"')

        for i, field in enumerate(fieldset['fields']):
            if field['id'] == 'location':
                initial_field = fieldset['fields'].pop(i)
                for location_field in [
                    'location_country',
                    'location_state',
                    'location_city',
                    'location_zip',
                    'location_address2',
                    'location_address1',
                ]:
                    fieldset['fields'].insert(i, {
                        'id': location_field,
                        'person_field': True,
                        'required': False if location_field == 'location_address2' else initial_field.get('required',
                                                                                                          True)
                    })
                continue
            if field.get('person_field') and field['id'] in all_person_field_names:
                continue
            elif not field.get('label') or not field.get('type'):
                raise ValidationError('Les champs doivent avoir un label et un type')
