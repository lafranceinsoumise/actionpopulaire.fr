from functools import reduce
from itertools import chain
from operator import or_

import iso8601
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Subquery, OuterRef, QuerySet
from django.urls import reverse
from django.utils.formats import localize
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.timezone import get_current_timezone
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import NumberParseException

from agir.people.models import Person, PersonForm, PersonEmail
from agir.people.person_forms.fields import (
    PREDEFINED_CHOICES,
    PREDEFINED_CHOICES_REVERSE,
)
from agir.people.person_forms.models import PersonFormSubmission


class PersonFormDisplay:
    NA_HTML_PLACEHOLDER = mark_safe('<em style="color: #999;">N/A</em>')
    NA_TEXT_PLACEHOLDER = "N/A"
    PUBLIC_FORMATS = {
        "bold": "<strong>{}</strong>",
        "italic": "<em>{}</em>",
        "normal": "{}",
    }
    admin_fields_label = ["ID", "Date de la réponse"]

    def get_admin_fields_label(self, form, html=True):
        if html:
            return ["Actions", *self.admin_fields_label, "Personne"]

        return [*self.admin_fields_label, "id_personne", "email"]

    def _get_form_and_submissions(self, submissions_or_form):
        if isinstance(submissions_or_form, PersonForm):
            form = submissions_or_form
            submissions = form.submissions.all().order_by("created")
        elif isinstance(submissions_or_form, QuerySet):
            submissions = submissions_or_form
            form = PersonForm.objects.get(submissions__in=submissions[:1])
        else:
            raise TypeError("`submissions_or_form")

        submissions = submissions.select_related("person").annotate(
            email=Subquery(
                PersonEmail.objects.filter(person_id=OuterRef("person__id"))
                .order_by("_bounced", "_order")
                .values("address")[:1]
            )
        )

        return form, submissions

    def _get_choice_label(self, field_descriptor, value, html=False):
        """Renvoie le libellé correct pour un champ de choix

        :param field_descriptor: le descripteur du champ
        :param value: la valeur prise par le champ
        :param html: s'il faut inclure du HTML ou non
        :return:
        """
        choices = field_descriptor["choices"]
        if isinstance(choices, str):
            pre_choices = PREDEFINED_CHOICES.get(choices)
            reverse_pre_choices = PREDEFINED_CHOICES_REVERSE.get(choices)
            if callable(pre_choices):
                if callable(reverse_pre_choices):
                    value = reverse_pre_choices(value) or value
                if hasattr(value, "get_absolute_url") and html:
                    return format_html(
                        '<a href="{0}">{1}</a>', value.get_absolute_url(), str(value)
                    )
                return str(value)
            choices = PREDEFINED_CHOICES.get(field_descriptor["choices"])
        else:
            choices = field_descriptor["choices"]
        choices = [
            (choice, choice) if isinstance(choice, str) else (choice[0], choice[1])
            for choice in choices
        ]
        try:
            return next(label for id, label in choices if id == value)
        except StopIteration:
            return value

    def _get_formatted_value(self, field, value, html=True, na_placeholder=None):
        """Récupère la valeur du champ pour les humains

        :param field:
        :param value:
        :param html:
        :param na_placeholder: la valeur à présenter pour les champs vides
        :return:
        """

        if value is None:
            if na_placeholder is not None:
                return na_placeholder

            if html:
                return self.NA_HTML_PLACEHOLDER

            return self.NA_TEXT_PLACEHOLDER

        field_type = field.get("type")

        if field_type in ["choice", "autocomplete_choice"] and "choices" in field:
            value = self._get_choice_label(field, value, html)
        elif field_type == "multiple_choice" and "choices" in field:
            if isinstance(value, list):
                value = " // ".join(
                    self._get_choice_label(field, v, html) for v in value
                )
        elif field_type == "person":
            try:
                value = str(Person.objects.get(id=value))
            except (ValidationError, ValueError, Person.DoesNotExist):
                value = value
        elif field_type == "datetime":
            date = iso8601.parse_date(value)
            value = localize(date.astimezone(get_current_timezone()))
        elif field_type == "datetimes":
            value = [
                localize(
                    iso8601.parse_date(datetime).astimezone(get_current_timezone())
                )
                for datetime in value
            ]
        elif field_type == "phone_number":
            try:
                phone_number = PhoneNumber.from_string(value)
                value = phone_number.as_international
            except NumberParseException:
                pass
        elif field_type == "file":
            if not isinstance(value, list):
                value = [value]

            if html:
                value = mark_safe(
                    "<br />".join(
                        [
                            format_html('<a href="{}">Fichier {}</a>', v, i + 1)
                            for i, v in enumerate(value)
                        ]
                    )
                )

        if isinstance(value, list):
            value = ", ".join(value)

        return value

    def _get_admin_fields(self, submissions, html=True):
        id_fields = [s.pk for s in submissions]

        for s in submissions:
            # copier l'email de façon à éviter une requête pour l'email PAR submission
            if s.person:
                s.person._email = s.email

        if html:
            dates = [
                submission.created.astimezone(get_current_timezone())
                .replace(microsecond=0)
                .isoformat()
                for submission in submissions
            ]
            action_field_template = (
                '<a href="{details}" title="Voir le détail">&#128269;</a>&ensp;'
                '<a href="{edit}" title="Modifier">&#x1F58A;&#xFE0F;️</a>&ensp;'
                '<a href="{delete}" title="Supprimer cette submission">&#x274c;</a>'
            )
            action_fields = [
                format_html(
                    action_field_template,
                    details=reverse(
                        "admin:people_personformsubmission_detail",
                        args=(submission.pk,),
                        urlconf="agir.api.admin_urls",
                    ),
                    edit=reverse(
                        "admin:people_personformsubmission_change",
                        args=(submission.pk,),
                        urlconf="agir.api.admin_urls",
                    ),
                    delete=reverse(
                        "admin:people_personformsubmission_delete",
                        args=(submission.pk,),
                        urlconf="agir.api.admin_urls",
                    ),
                )
                for submission in submissions
            ]

            person_field_template = '<a href="{link}">{person}</a>'
            person_fields = [
                format_html(
                    person_field_template,
                    link=settings.API_DOMAIN
                    + reverse(
                        "admin:people_person_change",
                        args=(submission.person_id,),
                        urlconf="agir.api.admin_urls",
                    ),
                    person=submission.person,
                )
                if submission.person
                else "Anonyme"
                for submission in submissions
            ]

            return [
                list(a) for a in zip(action_fields, id_fields, dates, person_fields)
            ]
        else:
            dates = [
                localize(submission.created.astimezone(get_current_timezone()))
                for submission in submissions
            ]
            id_persons = [
                (str(s.person.id) if s.person else "Anonyme") for s in submissions
            ]
            emails = [(s.person.email if s.person else "") for s in submissions]
            return [list(a) for a in zip(id_fields, dates, id_persons, emails)]

    def get_form_field_labels(self, form, fieldsets_titles=False):
        """Renvoie un dictionnaire associant id de champs et libellés à présenter

        Prend en compte tous les cas de figure :
        - champs dans le libellé est défini explicitement
        - champs de personnes dont le libellé n'est pas reprécisé...
        - etc.

        :param form:
        :param fieldsets_titles:
        :return:
        """
        field_information = {}

        person_fields = {f.name: f for f in Person._meta.get_fields()}

        for fieldset in form.custom_fields:
            for field in fieldset.get("fields", []):
                if field.get("person_field") and field["id"] in person_fields:
                    label = field.get(
                        "label",
                        capfirst(
                            getattr(
                                person_fields[field["id"]],
                                "verbose_name",
                                person_fields[field["id"]].name,
                            )
                        ),
                    )
                else:
                    label = field["label"]

                field_information[field["id"]] = (
                    format_html(
                        "{title}&nbsp;:<br>{label}",
                        title=fieldset["title"],
                        label=label,
                    )
                    if fieldsets_titles
                    else label
                )

        return field_information

    def get_formatted_submissions(
        self,
        submissions_or_form,
        html=True,
        include_admin_fields=True,
        resolve_labels=True,
        resolve_values=True,
        fieldsets_titles=False,
    ):
        if not submissions_or_form:
            return [], []

        form, submissions = self._get_form_and_submissions(submissions_or_form)

        if len(submissions) == 0:
            return [], []

        fields_dict = form.fields_dict

        labels = (
            self.get_form_field_labels(form, fieldsets_titles=fieldsets_titles)
            if resolve_labels
            else {}
        )

        full_data = [sub.data for sub in submissions]
        if resolve_values:
            full_values = [
                {
                    id: self._get_formatted_value(fields_dict[id], value, html)
                    if id in fields_dict
                    else value
                    for id, value in d.items()
                }
                for d in full_data
            ]
        else:
            full_values = full_data

        declared_fields = set(fields_dict)
        additional_fields = sorted(
            reduce(or_, (set(d) for d in full_data)).difference(declared_fields)
        )

        headers = [labels.get(id, id) for id in fields_dict] + additional_fields

        ordered_values = [
            [
                v.get(
                    i,
                    self.NA_HTML_PLACEHOLDER
                    if html and resolve_values
                    else self.NA_TEXT_PLACEHOLDER
                    if resolve_values
                    else "",
                )
                for i in chain(fields_dict, additional_fields)
            ]
            for v in full_values
        ]

        if include_admin_fields:
            admin_values = self._get_admin_fields(submissions, html)
            return (
                self.get_admin_fields_label(form, html=html) + headers,
                [
                    admin_values + values
                    for admin_values, values in zip(admin_values, ordered_values)
                ],
            )

        return headers, ordered_values

    def get_formatted_submission(
        self, submission, include_admin_fields=False, html=True
    ):
        data = submission.data
        fields_dict = submission.form.fields_dict
        labels = self.get_form_field_labels(submission.form)

        if include_admin_fields:
            res = [
                {
                    "title": "Administration",
                    "data": [
                        {"label": l, "value": v}
                        for l, v in zip(
                            self.get_admin_fields_label(submission.form, html=html),
                            self._get_admin_fields([submission], html=html)[0],
                        )
                    ],
                }
            ]
        else:
            res = []

        for fieldset in submission.form.custom_fields:
            fieldset_data = []
            for field in fieldset.get("fields", []):
                id = field["id"]
                if id in data:
                    label = labels[id]
                    value = self._get_formatted_value(field, data.get(id))
                    fieldset_data.append({"label": label, "value": value})
            res.append({"title": fieldset["title"], "data": fieldset_data})

        missing_fields = set(data).difference(set(fields_dict))

        missing_fields_data = []
        for id in sorted(missing_fields):
            missing_fields_data.append({"label": id, "value": data[id]})
        if len(missing_fields_data) > 0:
            res.append({"title": "Champs inconnus", "data": missing_fields_data})

        return res

    def _get_full_public_fields_definition(self, form):
        public_config = form.config.get("public", [])
        field_names = self.get_form_field_labels(form)

        return [
            {
                "id": f["id"],
                "label": f.get("label", field_names[f["id"]]),
                "format": f.get("format", "normal"),
            }
            for f in public_config
        ]

    def get_public_fields(self, submissions):
        if not submissions:
            return []

        only_one = False

        if isinstance(submissions, PersonFormSubmission):
            only_one = True
            submissions = [submissions]

        fields_dict = submissions[0].form.fields_dict
        public_fields_definition = self._get_full_public_fields_definition(
            submissions[0].form
        )

        public_submissions = []

        for submission in submissions:
            public_submissions.append(
                {
                    "date": submission.created,
                    "values": [
                        {
                            "label": pf["label"],
                            "value": format_html(
                                self.PUBLIC_FORMATS[pf["format"]],
                                self._get_formatted_value(
                                    fields_dict[pf["id"]], submission.data.get(pf["id"])
                                ),
                            ),
                        }
                        for pf in public_fields_definition
                    ],
                }
            )

        if only_one:
            return public_submissions[0]

        return public_submissions


default_person_form_display = PersonFormDisplay()
