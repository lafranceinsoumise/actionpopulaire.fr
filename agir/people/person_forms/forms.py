from pathlib import PurePath
from uuid import uuid4

import os
from copy import copy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.text import slugify
from django.utils.translation import gettext as _

from agir.lib.form_components import *
from agir.lib.form_mixins import MetaFieldsMixin
from agir.lib.token_bucket import TokenBucket
from agir.people.person_forms.field_groups import get_form_part
from .fields import is_actual_model_field, get_data_from_submission, get_form_field
from ..models import Person, PersonFormSubmission

check_person_email_bucket = TokenBucket("PersonFormPersonChoice", 10, 600)


class PersonTagChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description


class SuperHiddenDisplay(forms.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        return ""


class BasePersonForm(MetaFieldsMixin, forms.ModelForm):
    """base form class for using PersonForm models

    It should not be used by itself, but only with people.actions.get_people_form_class
    """

    person_form_instance = None
    hidden_fields = {}
    is_submission_edition = False

    def get_meta_fields(self):
        return [
            field["id"]
            for fieldset in self.person_form_instance.custom_fields
            for field in fieldset.get("fields", [])
            if field.get("person_field") and not is_actual_model_field(field)
        ]

    def __init__(self, *args, query_params=None, data=None, **kwargs):
        self.submission = kwargs.pop("submission", None)

        if self.person_form_instance.config.get("hidden_fields"):
            self.hidden_fields = {
                desc["id"]: desc
                for desc in self.person_form_instance.config["hidden_fields"]
            }

        # s'assurer que les informations des champs hidden fields viennent forcément de GET
        if data is not None and query_params is not None:
            data = copy(data)  # to make it mutable
            for f in self.hidden_fields:
                data[f] = query_params.get(f)

        super().__init__(*args, data=data, **kwargs)

        if self.person_form_instance.editable and self.submission is not None:
            for id, value in get_data_from_submission(self.submission).items():
                self.initial[id] = value
            self.is_submission_edition = True

        parts = []

        # lors de la création et du test du formulaire, celui-ci n'a pas encore d'ID, et on ne peut pas manipuler
        # ses tags
        if not self.person_form_instance._state.adding:
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
        if self.person_form_instance.campaign_template is not None:
            self.helper.add_input(
                Submit(
                    "preview",
                    "Prévisualiser l'email",
                    formtarget="_blank",
                    css_class="btn btn-primary btn-block margintopmore btn-submit",
                )
            )

        self.helper.add_input(
            Submit(
                "submit",
                self.person_form_instance.submit_label,
                disabled=self.person_form_instance.campaign_template is not None,
                css_class="btn btn-primary btn-block margintopmore btn-submit",
            )
        )
        self.helper.layout = Layout()

        if self.person_form_instance.custom_fields:
            self.parts = [
                get_form_part(part) for part in self.person_form_instance.custom_fields
            ]
        else:
            self.parts = []

        for part in self.parts:
            part.set_up_fields(self, self.is_submission_edition)

        self.update_meta_initial()

        # Vérifier les potentiels risques de sécurité ici (forger un lien qui préremplit un formulaire
        # différement de ce qu'on aurait souhaité).
        if query_params is not None:
            for field in self.fields:
                if field in query_params:
                    self.initial[field] = query_params[field]

        for id, field_desc in self.hidden_fields.items():
            self.fields[id] = get_form_field(
                {**field_desc, "widget": SuperHiddenDisplay()},
                is_submission_edition=self.is_submission_edition,
            )

    def clean(self):
        cleaned_data = super().clean()

        for id, field_descriptor in self.person_form_instance.fields_dict.items():
            if field_descriptor.get("type") == "person":
                if not check_person_email_bucket.has_tokens(self.instance.pk):
                    self.add_error(
                        id,
                        ValidationError(
                            "Vous avez fait trop d'erreurs. Par sécurité, vous devez attendre avant d'essayer d'autres adresses emails."
                        ),
                    )
                elif (
                    not field_descriptor.get("allow_self")
                    and cleaned_data.get(id) == self.instance.pk
                ):
                    self.add_error(
                        id,
                        ValidationError(
                            "Vous ne pouvez pas vous indiquer vous-mêmes.",
                            code="selected_self",
                        ),
                    )

            if (
                self.is_submission_edition
                and not field_descriptor.get("editable", False)
                and cleaned_data.get(id) != self.initial.get(id)
            ):
                self.add_error(
                    id, ValidationError("Ce champ ne peut pas être modifié.")
                )

        for part in self.parts:
            if hasattr(part, "clean"):
                cleaned_data = part.clean(self, cleaned_data)

        return cleaned_data

    @property
    def submission_data(self):
        data = {}
        for part in self.parts:
            data.update(part.collect_results(self.cleaned_data))

        for f in self.hidden_fields:
            data[f] = self.cleaned_data[f]

        return data

    def save(self, commit=True):
        # We never want to create a new Person
        if not self.instance._state.adding:
            return super().save(commit=commit)
        return self.save_submission()

    def save_submission(self, person=None):
        """
        Can be used to save a submission without saving the Person
        """

        data = self.submission_data

        # making sure files are saved
        for key, value in data.items():
            if isinstance(value, File) and key in self.files:
                data[key] = [self._save_file(f, key) for f in self.files.getlist(key)]
            elif isinstance(value, File):
                data[key] = [self._save_file(value, key)]

        if self.submission is not None:
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

    def _save_file(self, file, field_name):
        form_slug = self.person_form_instance.slug
        extension = os.path.splitext(file.name)[1].lower()
        path = str(
            PurePath("person_forms")
            / form_slug
            / slugify(field_name)
            / (str(uuid4()) + extension)
        )
        stored_file = default_storage.save(path, file)
        return default_storage.url(stored_file)

    class Meta:
        model = Person
        fields = []
