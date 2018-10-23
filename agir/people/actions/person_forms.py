import os
from uuid import uuid4
from typing import List, Dict, Tuple

from pathlib import PurePath
from django import forms
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from phonenumber_field.formfields import PhoneNumberField

from agir.lib.form_components import *
from ..form_mixins import MetaFieldsMixin

from ..models import Person, PersonFormSubmission


all_person_field_names = [field.name for field in Person._meta.get_fields()]


class NotRequiredByDefaultMixin:
    def __init__(self, *args, required=False, **kwargs):
        super().__init__(*args, required=required, **kwargs)


class LongTextField(forms.CharField):
    widget = forms.Textarea


class ChoiceField(forms.ChoiceField):
    def __init__(self, *, choices, default_label=None, required=True, **kwargs):
        if default_label is None:
            default_label = '---' if required else _("Non applicable / ne souhaite pas répondre")

        choices = [('', default_label), *choices]

        super().__init__(choices=choices, required=required, **kwargs)


class MultipleChoiceField(NotRequiredByDefaultMixin, forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple


class BooleanField(NotRequiredByDefaultMixin, forms.BooleanField):
    pass


def save_file(file, form_slug):
    extension = os.path.splitext(file.name)[1].lower()
    path = str(PurePath('person_forms') / form_slug / (str(uuid4()) + extension))
    default_storage.save(path, file)
    return path


@deconstructible
class FileSizeValidator:
    message = _("Ce fichier est trop gros. Seuls les fichiers de moins de %(max_size) sont acceptés.")
    code = 'file_too_big'

    def __init__(self, max_size, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        self.max_size = max_size

    def __call__(self, value):
        if value.size > self.max_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    'max_size': filesizeformat(self.max_size)
                }
            )


class FileField(forms.FileField):
    def __init__(self, *, max_size=None, allowed_extensions=None, validators=None, **kwargs):
        validators = validators or []
        if allowed_extensions:
            validators.append(FileExtensionValidator(allowed_extensions))
        if max_size:
            validators.append(FileSizeValidator(max_size))

        super().__init__(validators=validators, **kwargs)


class FieldSet:
    def __init__(self, title: str, fields: List[Dict], **kwargs):
        self.title = title
        self.fields = fields

    def set_up_fields(self, form):
        for field_descriptor in self.fields:
            if is_actual_model_field(field_descriptor):
                # by default person fields are required
                form.fields[field_descriptor['id']].required = True

                if field_descriptor['id'] == 'date_of_birth':
                    form.fields[field_descriptor['id']].help_text = _('Format JJ/MM/AAAA')
            else:
                form.fields[field_descriptor['id']] = get_form_field(field_descriptor)

        form.helper.layout.append(
            Fieldset(self.title, *(Row(FullCol(field_descriptor['id'])) for field_descriptor in self.fields))
        )

    def collect_results(self, cleaned_data):
        return {field_descriptor['id']: cleaned_data[field_descriptor['id']] for field_descriptor in self.fields}


class DoubleEntryTable:
    def __init__(self, *, title, id, intro=None, row_name, rows: List[Tuple[str, str]], fields: List[Dict], **kwargs):
        self.title = title
        self.intro = intro
        self.id = id
        self.row_name = row_name
        self.rows = rows
        self.fields = fields

    def get_id(self, row_id, field_id):
        return f"{self.id}:{row_id}:{field_id}"

    def get_header_row(self):
        return f"<tr><th>{self.row_name}</th>" + "".join("<th>{}</th>".format(col['label']) for col in self.fields) + '</tr>'

    def get_row(self, form, row_id, row_label):
        return f"<tr><th>{row_label}</th>" + "".join("<td>{}</td>".format(form[self.get_id(row_id, col['id'])]) for col in self.fields) + '</tr>'

    def set_up_fields(self, form: forms.Form):
        for row_id, row_label in self.rows:
            for field_descriptor in self.fields:
                id = self.get_id(row_id, field_descriptor['id'])
                field = get_form_field(field_descriptor)
                form.fields[id] = field

        intro = f"<p>{self.intro}</p>" if self.intro else ""

        text = intro + f"""
        <table class="table">
        <thead>
        {self.get_header_row()}
        </thead>
        <tbody>""" + ''.join(self.get_row(form, row_id, row_label) for row_id, row_label in self.rows) + """
        </tbody>
        </table>
        """

        form.helper.layout.append(Fieldset(self.title, HTML(text)))

    def collect_results(self, cleaned_data):
        return {
            self.get_id(row_id, col['id']): cleaned_data[self.get_id(row_id, col['id'])]
            for row_id, row_label in self.rows for col in self.fields
        }


FIELDS = {
    'short_text': forms.CharField,
    'long_text': LongTextField,
    'choice': ChoiceField,
    'multiple_choice': MultipleChoiceField,
    'email_address': forms.EmailField,
    'phone_number': PhoneNumberField,
    'url': forms.URLField,
    'file': FileField,
    'boolean': BooleanField,
    'integer': forms.IntegerField
}

PARTS = {
    'fieldset': FieldSet,
    'double_entry': DoubleEntryTable,
}


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

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Envoyer'))
        self.helper.layout = Layout()

        if self.person_form_instance.custom_fields:
            self.parts = [
                PARTS[part.get('type', 'fieldset')](**part) for part in self.person_form_instance.custom_fields
            ]
        else:
            self.parts = []

        for part in self.parts:
            part.set_up_fields(self)

    @property
    def submission_data(self):
        data = {}
        for part in self.parts:
            data.update(part.collect_results(self.cleaned_data))
        return data

    def save_submission(self, person):
        if person is None:
            person = self.instance

        data = self.submission_data

        # making sure files are saved
        for key, value in data.items():
            if isinstance(value, File):
                data[key] = save_file(value, self.person_form_instance.slug)

        self.submission = PersonFormSubmission.objects.create(
            person=person,
            form=self.person_form_instance,
            data=data
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


def is_actual_model_field(field_descriptor):
    return field_descriptor.get('person_field', False) and field_descriptor['id'] in all_person_field_names


def get_form_field(field_descriptor: dict):
    field_descriptor = field_descriptor.copy()
    field_type = field_descriptor.pop('type')
    field_descriptor.pop('id')
    field_descriptor.pop('person_field', None)

    klass = FIELDS.get(field_type)

    if klass:
        return klass(**field_descriptor)

    raise ValueError(f"Unkwnown field type: '{field_type}'")


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
