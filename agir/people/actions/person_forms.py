from functools import reduce
from itertools import chain
from operator import or_

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from django.utils.formats import date_format
from django.utils.safestring import mark_safe

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import NumberParseException

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


def _get_choice_label(choices, value):
    try:
        return next(label for id, label in choices if id == value)
    except StopIteration:
        return value


def _get_formatted_value(field, value, html=True):
    field_type = field.get('type')

    if field_type == 'choice' and 'choices' in field:
        return _get_choice_label(field['choices'], value)
    elif field_type == 'multiple_choice' and 'choices' in field:
        if isinstance(value, list):
            return [_get_choice_label(field['choices'], v) for v in value]
        else:
            return value
    elif field_type == 'phone_number':
        try:
            phone_number = PhoneNumber.from_string(value)
            return phone_number.as_international
        except NumberParseException:
            return value
    elif field_type == 'file':
        url = settings.FRONT_DOMAIN + settings.MEDIA_URL + value
        if html:
            return format_html(
                '<a href="{}">Accéder au fichier</a>',
                url
            )
        else:
            return url

    return value


NA_PLACEHOLDER = mark_safe('<em style="color: #999;">N/A</em>')

ADMIN_FIELDS_LABELS = ['ID', 'Personne', 'Date de la réponse']


def _get_admin_fields(submission, html=True):
    return [
        format_html(
            '<a href="{}" title="Supprimer cette submission">{} X</a>',
            reverse('admin:people_personformsubmission_delete', args=(submission.pk,)),
            submission.pk
        ) if html else submission.pk,
        format_html(
            '<a href="{}">{}</a>',
            settings.API_DOMAIN + reverse('admin:people_person_change', args=(submission.person_id,)),
            submission.person.email) if html else submission.person.email,
        date_format(submission.created)
    ]


def get_formatted_submissions(submissions, include_admin_fields=True, html=True):
    if not submissions:
        return [], []

    form = submissions[0].form
    field_dict = form.fields_dict

    labels = get_form_field_labels(form)

    full_data = [sub.data for sub in submissions]
    full_values = [{id: _get_formatted_value(field_dict[id], value, html) for id, value in d.items()} for d in full_data]

    declared_fields = set(field_dict)
    additional_fields = sorted(reduce(or_, (set(d) for d in full_data)).difference(declared_fields))

    headers = [labels[id] for id in field_dict] + additional_fields

    ordered_values = [[v.get(i, NA_PLACEHOLDER) for i in chain(field_dict, additional_fields)] for v in full_values]

    if include_admin_fields:
        admin_values = [_get_admin_fields(s, html) for s in submissions]
        return ADMIN_FIELDS_LABELS + headers, [admin_values + values for admin_values, values in zip(admin_values, ordered_values)]

    return headers, ordered_values


def get_formatted_submission(submission, include_admin_fields=False):
    data = submission.data
    field_dicts = submission.form.fields_dict
    labels = get_form_field_labels(submission.form)

    if include_admin_fields:
        res = [{'label': l, 'value': v} for l, v in zip(ADMIN_FIELDS_LABELS, _get_admin_fields(submission))]
    else:
        res = []

    for id, field in field_dicts.items():
        if id in data:
            label = labels[id]
            value = _get_formatted_value(field, data[id]) if id in data else NA_PLACEHOLDER
            res.append({'label': label, 'value': value})

    missing_fields = set(data).difference(set(field_dicts))

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
