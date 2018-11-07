from django import forms
from django.core.exceptions import ValidationError

from ..models import Person

from ..person_forms.forms import BasePersonForm
from ..person_forms.fields import is_actual_model_field


def get_people_form_class(person_form_instance, base_form=BasePersonForm):
    """Returns the form class for the specific person_form_instance

    :param person_form_instance: the person_form model object for which the form class must be generated
    :param base_form: an optional base form to use instead of the default BasePersonForm
    :return: a form class that can be used to generate a form for the person_form_instance
    """
    # the list of 'person_fields' that will also be saved on the person model when saving the form
    form_person_fields = [field['id'] for fieldset in person_form_instance.custom_fields for field in fieldset['fields']
                          if is_actual_model_field(field)]

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
            if is_actual_model_field(field):
                continue
            elif not field.get('label') or not field.get('type'):
                raise ValidationError('Les champs doivent avoir un label et un type')
