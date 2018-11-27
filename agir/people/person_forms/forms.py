import os
from uuid import uuid4

from pathlib import PurePath
from django import forms
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper

from agir.lib.form_components import *
from agir.people.person_forms.field_groups import get_form_part

from ..form_mixins import MetaFieldsMixin
from ..models import Person, PersonFormSubmission
from .fields import is_actual_model_field, get_data_from_submission


class PersonTagChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description


class BasePersonForm(MetaFieldsMixin, forms.ModelForm):
    """base form class for using PersonForm models

    It should not be used by itself, but only with people.actions.get_people_form_class
    """

    person_form_instance = None
    is_edition = False

    def get_meta_fields(self):
        return [
            field["id"]
            for fieldset in self.person_form_instance.custom_fields
            for field in fieldset["fields"]
            if field.get("person_field") and not is_actual_model_field(field)
        ]

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop("submission", None)

        super().__init__(*args, **kwargs)

        if self.person_form_instance.editable:
            self.submission = (
                self.submission
                or PersonFormSubmission.objects.filter(
                    person=self.instance, form=self.person_form_instance
                )
                .order_by("modified")
                .last()
            )

            if self.submission is not None:
                for id, value in get_data_from_submission(self.submission).items():
                    self.initial[id] = value
                self.is_edition = True

        parts = []

        self.tag_queryset = self.person_form_instance.tags.all()

        if len(self.tag_queryset) > 1:
            self.fields["tag"] = PersonTagChoiceField(
                queryset=self.tag_queryset,
                to_field_name="label",
                required=True,
                label=self.person_form_instance.main_question,
            )
            parts.append(Fieldset(_("Ma situation"), Row(FullCol("tag"))))
        elif len(self.tag_queryset) == 1:
            self.tag = self.tag_queryset[0]

        opts = self._meta
        if opts.fields:
            for f in opts.fields:
                self.fields[f].required = True

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Envoyer"))
        self.helper.layout = Layout()

        if self.person_form_instance.custom_fields:
            self.parts = [
                get_form_part(part) for part in self.person_form_instance.custom_fields
            ]
        else:
            self.parts = []

        for part in self.parts:
            part.set_up_fields(self, self.is_edition)

    def clean(self):
        if not self.is_edition:
            return super().clean()

        cleaned_data = super().clean()

        for id, field_descriptor in self.person_form_instance.fields_dict.items():
            if not field_descriptor.get("editable", False) and cleaned_data.get(
                id
            ) != self.initial.get(id):
                self.add_error(
                    id, ValidationError("Ce champ ne peut pas être modifié.")
                )

        return cleaned_data

    @property
    def submission_data(self):
        data = {}
        for part in self.parts:
            data.update(part.collect_results(self.cleaned_data))
        return data

    def save_submission(self, person):
        """
        Can be used to save a submission without saving the Person
        """
        if person is None:
            person = self.instance

        data = self.submission_data

        # making sure files are saved
        for key, value in data.items():
            if isinstance(value, File):
                data[key] = self._save_file(value)

        if self.person_form_instance.editable:
            if self.submission is None:
                self.submission, created = PersonFormSubmission.objects.get_or_create(
                    person=person, form=self.person_form_instance
                )
            self.submission.data = data
            self.submission.save()
        else:
            self.submission = PersonFormSubmission.objects.create(
                person=person, form=self.person_form_instance, data=data
            )

        return self.submission

    def _save_m2m(self):
        if "tag" in self.cleaned_data:
            self.instance.tags.add(self.cleaned_data["tag"])
        elif hasattr(self, "tag"):
            self.instance.tags.add(self.tag)

        self.save_submission(self.instance)

    def _save_file(self, file):
        form_slug = self.person_form_instance.slug
        extension = os.path.splitext(file.name)[1].lower()
        path = str(PurePath("person_forms") / form_slug / (str(uuid4()) + extension))
        default_storage.save(path, file)
        return path

    class Meta:
        model = Person
        fields = []
