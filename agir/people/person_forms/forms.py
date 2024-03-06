import os
from pathlib import PurePath
from uuid import uuid4

from django import forms
from django.core.files import File
from django.core.files.storage import default_storage
from django.forms import formset_factory
from django.template.loader import get_template
from django.utils.text import slugify

from agir.lib.token_bucket import TokenBucket
from .fields import (
    is_actual_model_field,
    get_data_from_submission,
    get_form_field,
    FileList,
)
from ..models import PersonFormSubmission

check_person_email_bucket = TokenBucket("PersonFormPersonChoice", 10, 600)


class SuperHiddenDisplay(forms.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        return ""


class PersonFormController:
    """Contrôleur pour les formulaires de personnes.

    Cette classe est notamment responsable pour la gestion :

    - des champs cachés, qui doivent être « peuplés » à partir des champs GET de l'URL, et non du POST
    - de la création du formulaire principal, et des FormSet correspondant à chaque fieldset multiple
    - de l'orchestration de la validation générale.

    """

    def __init__(
        self,
        person_form,
        instance=None,
        data=None,
        files=None,
        query_params=None,
        submission=None,
        initial=None,
        base_class=forms.Form,
        **kwargs,
    ):
        self.data = data
        self.files = files
        self.query_params = query_params
        self.base_class = base_class
        self.initial = initial
        self.kwargs = kwargs

        self.tags_to_add = []
        self.errors = []

        self.person_form_instance = person_form
        self.submitter = instance

        self.submission = submission
        self.edition = bool(submission)

        self.description = self.get_description()

        self.main_form = self.get_main_form()
        self.formsets = self.get_formsets()
        self.hidden_form = self.get_hidden_form()

        if self.hidden_form and not self.hidden_form.is_valid():
            self.errors.append("Le lien que vous avez suivi est invalide.")

    def get_description(self):
        """deep clone form description to avoid issues with modifying it"""
        main_field = None

        if not self.person_form_instance._state.adding:
            main_field = self.person_form_instance.main_question_field
            all_tags = list(self.person_form_instance.tags.all())
            # if main_question is not specified or only one tag is selected: automatically add the tag(s)
            if len(all_tags) <= 1 or not main_field:
                self.tags_to_add += all_tags

        description = [
            *([main_field] if main_field else []),
            *[
                {**fieldset, "fields": [{**f} for f in fieldset.get("fields", [])]}
                for fieldset in self.person_form_instance.custom_fields
            ],
        ]

        return description

    def get_main_form_fields(self):
        return [
            desc
            for fieldset in self.description
            if not fieldset.get("multiple", False)
            for desc in fieldset["fields"]
        ]

    def get_person_fields(self):
        return [
            desc
            for desc in self.get_main_form_fields()
            if desc.get("person_field", False)
        ]

    def get_main_form_initial(self):
        initial = {}

        # Il faut initialiser les person fields (y compris les champs meta) à partir de la valeur de l'objet
        if self.submitter:
            for field in self.get_person_fields():
                if is_actual_model_field(field):
                    initial[field["id"]] = getattr(self.submitter, field["id"])
                else:
                    initial[field["id"]] = self.submitter.meta.get(field["id"])

        # Si nous sommes dans le cas d'une édition, préremplir les champs avec les valeurs actuelles
        if self.edition:
            for id, value in get_data_from_submission(self.submission).items():
                initial[id] = value

        if self.initial:
            initial.update(self.initial)

        return initial

    def get_main_form(self):
        fields_descriptors = self.get_main_form_fields()
        fields = {
            f["id"]: get_form_field(
                f,
                edition=self.edition,
                instance=self.submitter,
            )
            for f in fields_descriptors
        }

        fields["_controller"] = self

        form_klass = type("MainForm", (self.base_class,), fields)

        form = form_klass(
            data=self.data,
            files=self.files,
            initial=self.get_main_form_initial(),
            **self.kwargs,
        )

        return form

    def get_formsets(self):
        formset_fieldsets = [
            fs
            for fs in self.person_form_instance.custom_fields
            if fs.get("multiple", False)
        ]
        extra = 0 if self.edition else 1

        formsets = {}

        for fieldset in formset_fieldsets:
            # d'abord créer la classe de formulaire
            form_klass = type(
                f"{fieldset['id']}Form",
                (forms.Form,),
                {f["id"]: get_form_field(f, self.edition) for f in fieldset["fields"]},
            )
            formset_klass = formset_factory(form_klass, extra=extra)

            data = self.data and {
                k: v for k, v in self.data.items() if k.startswith(f'{fieldset["id"]}-')
            }
            initial = None
            if self.edition:
                initial = self.submission.data.get(fieldset["id"])

            formsets[fieldset["id"]] = formset_klass(
                data=data, initial=initial, prefix=fieldset["id"]
            )

        return formsets

    def get_hidden_form(self):
        if self.query_params is None:
            return None

        hidden_fields = {
            desc["id"]: get_form_field(desc)
            for desc in self.person_form_instance.config.get("hidden_fields", [])
        }
        form_klass = type("HiddenForm", (forms.Form,), hidden_fields)
        return form_klass(
            data=self.query_params,
        )

    def render(self):
        for fieldset in self.description:
            if fieldset.get("multiple", False):
                fieldset["formset"] = self.formsets[fieldset["id"]]
            else:
                for field in fieldset["fields"]:
                    field["field_instance"] = self.main_form[field["id"]]

        template = get_template("person_forms/render.html")

        context = {"controller": self, "fieldsets": self.description}
        return template.render(context=context)

    def is_valid(self):
        if (
            not self.main_form.is_valid()
            or not self.hidden_form.is_valid()
            or any(not formset.is_valid() for formset in self.formsets)
        ):
            return False

        self.cleaned_data = cleaned_data = {}
        cleaned_data.update(self.hidden_form.cleaned_data)
        cleaned_data.update(self.main_form.cleaned_data)

        for formset in self.formsets:
            cleaned_data[formset.prefix] = formset.clean()

        if any(
            field.get("type") == "person"
            for fieldset in self.description
            for field in fieldset.get("fields", [])
        ):
            if not check_person_email_bucket.has_tokens(self.submitter.pk):
                self.errors.append(
                    "Vous avez fait trop de tentatives de remplissage de ce formulaire. Veuillez patienter un peu avant de recommencer."
                )
                return False

        return True

    def save_submitter(self, person=None):
        """Save the submitter information from the person_fields"""
        person = person or self.submitter

        for desc in self.get_person_fields():
            if desc["id"] in self.cleaned_data:
                setattr(person, desc["id"], self.cleaned_data[desc["id"]])
            elif desc["type"] == "person_tag":
                field_tags = self.cleaned_data[desc["id"]]
                if field_tags:
                    self.tags_to_add.extend(
                        field_tags if isinstance(field_tags, list) else [field_tags]
                    )

        person.save()

        if self.tags_to_add:
            # Fields of type tags are only used to ADD tags to a person (except for person_form_instance tags
            # which are meant to be exclusive and thus are all removed before addition)
            other_tags = list(
                person.tags.difference(self.person_form_instance.tags.all())
            )

            person.tags.set(other_tags + self.tags_to_add)

        return person

    def save_submission(self, person=None, **kwargs):
        """Saves a submission instance with the information from the forms"""

        data = self.cleaned_data or {}

        # making sure files are saved
        for key, value in data.items():
            if isinstance(value, File) and key in self.files:
                data[key] = [self._save_file(f, key) for f in self.files.getlist(key)]
            elif isinstance(value, File):
                data[key] = [self._save_file(value, key)]
            elif isinstance(value, FileList):
                data[key] = [self._save_file(v, key) for v in value]

        data.update(kwargs)

        if self.submission is not None:
            self.submission.data = data
            self.submission.save()
        else:
            person = person or self.submitter
            self.submission = PersonFormSubmission.objects.create(
                person=person, form=self.person_form_instance, data=data
            )

        return self.submission

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
