import os
from uuid import uuid4

from pathlib import PurePath
from django import forms
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper

from agir.lib.form_components import *
from agir.people.person_forms.field_groups import get_form_part

from ..form_mixins import MetaFieldsMixin
from ..models import Person, PersonFormSubmission
from .fields import is_actual_model_field


class PersonTagChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description


class BasePersonForm(MetaFieldsMixin, forms.ModelForm):
    person_form_instance = None

    def get_meta_fields(self):
        return [field['id']
                for fieldset in self.person_form_instance.custom_fields
                for field in fieldset['fields']
                if field.get('person_field') and not is_actual_model_field(field)]

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
                get_form_part(part) for part in self.person_form_instance.custom_fields
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
                data[key] = self._save_file(value)

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

    def _save_file(self, file):
        form_slug = self.person_form_instance.slug
        extension = os.path.splitext(file.name)[1].lower()
        path = str(PurePath('person_forms') / form_slug / (str(uuid4()) + extension))
        default_storage.save(path, file)
        return path

    class Meta:
        model = Person
        fields = []
