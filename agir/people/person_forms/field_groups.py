from itertools import product
from typing import List, Dict, Tuple

from crispy_forms.layout import Fieldset, Row
from django import forms
from django.utils.functional import lazy
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from agir.lib.form_components import *
from agir.people.person_forms.fields import is_actual_model_field, get_form_field


class FieldGroup:
    def __init__(self, **kwargs):
        pass

    def set_up_fields(self, form, is_edition):
        raise NotImplementedError()

    def collect_results(self, cleaned_data):
        raise NotImplementedError()

    def clean(self, form, cleaned_data):
        return cleaned_data


class FieldSet(FieldGroup):
    def __init__(
        self, title: str, fields: List[Dict], intro_html: str = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.fields = fields
        self.intro_html = intro_html

    def set_up_fields(self, form, is_edition):
        for field_descriptor in self.fields:
            if is_actual_model_field(field_descriptor):
                # Allow overriding of default form field by setting type on the field config
                if field_descriptor.get("type"):
                    if not field_descriptor.get("label"):
                        field_descriptor["label"] = str(
                            form.fields[field_descriptor["id"]].label
                        )
                    form.fields[field_descriptor["id"]] = get_form_field(
                        field_descriptor, is_edition, form.instance
                    )

                # by default person fields are required
                form.fields[field_descriptor["id"]].required = field_descriptor.get(
                    "required", True
                )
                if is_edition:
                    form.fields[field_descriptor["id"]].disabled = (
                        not field_descriptor.get("editable", False)
                    )

                if field_descriptor["id"] == "date_of_birth":
                    form.fields[field_descriptor["id"]].help_text = _(
                        "Format JJ/MM/AAAA"
                    )

                if field_descriptor["id"] == "newsletters":
                    form.fields[field_descriptor["id"]].initial = (
                        form.instance.newsletters
                    )

            else:
                form.fields[field_descriptor["id"]] = get_form_field(
                    field_descriptor, is_edition, form.instance
                )

        fields = (
            Row(FullCol(field_descriptor["id"])) for field_descriptor in self.fields
        )

        if self.intro_html is not None:
            fields = (HTML(self.intro_html), *fields)

        form.helper.layout.append(Fieldset(self.title, *fields))

    def collect_results(self, cleaned_data):
        return {
            field_descriptor["id"]: cleaned_data[field_descriptor["id"]]
            for field_descriptor in self.fields
        }


class CrossTable(FieldGroup):
    def __init__(
        self,
        *,
        title,
        intro=None,
        field,
        rows=None,
        columns=None,
        subset=None,
        minimum_required=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.intro = intro
        self.field_descriptor = field
        self.rows = rows
        self.columns = columns
        self.subset = subset
        self.minimum_required = minimum_required
        self.fake_field_id = field["id"] + "_hidden"

        if field.get("person_field"):
            raise ValueError(
                "Pas possible d'utiliser des champs de personne dans les cross tables"
            )

        if self.rows is None:
            if self.subset is None:
                raise ValueError(
                    "L'un des paramètres 'rows' ou 'subset' doit être défini"
                )
            seen = set()
            self.rows = [r for r, c in self.subset if not (r in seen or seen.add(r))]
        if self.columns is None:
            if self.subset is None:
                raise ValueError(
                    "L'un des paramètres 'columns' ou 'subset' doit être défini"
                )
            seen = set()
            self.columns = [c for r, c in self.subset if not (c in seen or seen.add(c))]

        self.subset = set(tuple(c) for c in self.subset)

    def get_id(self, row_id, column_id):
        return f"{self.field_descriptor['id']}_{row_id}_{column_id}"

    def get_header_row(self):
        return format_html(
            "<tr><th></th>{}</tr>",
            format_html_join(
                "",
                '<th style="text-align: center;">{}</th>',
                ((c,) for c in self.columns),
            ),
        )

    def get_row(self, form, row):
        return format_html(
            '<tr><th style="text-align: right;">{row_name}</th>{row_content}</tr>',
            row_name=row,
            row_content=format_html_join(
                "\n",
                '<td><label style="display:block;margin:0;">{}</label></td>',
                (
                    (
                        (mark_safe((form[self.get_id(row, col)])),)
                        if self.subset is None or (row, col) in self.subset
                        else ("",)
                    )
                    for col in self.columns
                ),
            ),
        )

    def display_errors(self, form: forms.Form):
        errors = [err for err in form.errors.get(self.fake_field_id, [])]

        it = self.subset or product(self.rows, self.columns)
        errors.extend(
            f"{c} {r} : {err}"
            for r, c in it
            for err in form.errors.get(self.get_id(r, c), [])
        )

        if errors:
            return format_html(
                '<div class="has-error"><ul class="help-block">{all_errors}</ul></div>',
                all_errors=format_html_join(
                    "\n", "<li>{}</li>", ((e,) for e in errors)
                ),
            )
        return ""

    def render_part(self):
        intro = f"<p>{self.intro}</p>" if self.intro else ""

        return (
            f"""
        {intro}
        {self.display_errors(self.form)}
        <table class="table" style="text-align: center;">
        <thead>
        {self.get_header_row()}
        </thead>
        <tbody>"""
            + "".join(self.get_row(self.form, row) for row in self.rows)
            + """
        </tbody>
        </table>
        """
        )

    def set_up_fields(self, form: forms.Form, is_edition):
        self.form = form
        it = self.subset or product(self.rows, self.columns)

        # ajoute un faux champ pour y mettre les erreurs de table
        fake_field = forms.Field(required=False)
        form.fields[self.fake_field_id] = fake_field

        for row, col in it:
            id = self.get_id(row, col)
            field_descriptor = {**self.field_descriptor, "id": id}
            field = get_form_field(field_descriptor, is_edition, form.instance)
            form.fields[id] = field

        form.helper.layout.append(Fieldset(self.title, HTML(lazy(self.render_part)())))

    def clean(self, form: forms.Form, cleaned_data):
        if self.minimum_required is not None:
            all_fields = self.subset or list(product(self.rows, self.columns))
            has_error = any(form.has_error(self.get_id(r, c)) for r, c in all_fields)
            if has_error:
                return cleaned_data

            n_values = sum(
                1 for r, c in all_fields if cleaned_data.get(self.get_id(r, c))
            )

            if n_values < self.minimum_required:
                form.add_error(
                    self.fake_field_id,
                    f"Vous devez remplir au moins {self.minimum_required} champs.",
                )
            return cleaned_data

    def collect_results(self, cleaned_data):
        it = self.subset or product(self.rows, self.columns)
        return {
            self.get_id(row, col): cleaned_data[self.get_id(row, col)]
            for row, col in it
        }


class DoubleEntryTable(FieldGroup):
    def __init__(
        self,
        *,
        title,
        id,
        intro=None,
        row_name,
        rows: List[Tuple[str, str]],
        fields: List[Dict],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.intro = intro
        self.id = id
        self.row_name = row_name
        self.rows = rows
        self.fields = fields

    def get_id(self, row_id, field_id):
        return f"{self.id}:{row_id}:{field_id}"

    def get_header_row(self):
        return (
            f"<tr><th>{self.row_name}</th>"
            + "".join("<th>{}</th>".format(col["label"]) for col in self.fields)
            + "</tr>"
        )

    def get_row(self, form, row_id, row_label):
        return (
            f"<tr><th>{row_label}</th>"
            + "".join(
                "<td>{}</td>".format(form[self.get_id(row_id, col["id"])])
                for col in self.fields
            )
            + "</tr>"
        )

    def set_up_fields(self, form: forms.Form, is_edition):
        for row_id, row_label in self.rows:
            for field_descriptor in self.fields:
                id = self.get_id(row_id, field_descriptor["id"])
                field = get_form_field(field_descriptor, is_edition, form.instance)
                form.fields[id] = field

        intro = f"<p>{self.intro}</p>" if self.intro else ""

        text = (
            intro
            + f"""
        <table class="table">
        <thead>
        {self.get_header_row()}
        </thead>
        <tbody>"""
            + "".join(
                self.get_row(form, row_id, row_label) for row_id, row_label in self.rows
            )
            + """
        </tbody>
        </table>
        """
        )

        form.helper.layout.append(Fieldset(self.title, HTML(text)))

    def collect_results(self, cleaned_data):
        return {
            self.get_id(row_id, col["id"]): cleaned_data[self.get_id(row_id, col["id"])]
            for row_id, row_label in self.rows
            for col in self.fields
        }


PARTS = {
    "fieldset": FieldSet,
    "cross_table": CrossTable,
    "double_entry": DoubleEntryTable,
}


def get_form_part(part):
    return PARTS[part.get("type", "fieldset")](**part)
