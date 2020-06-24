from itertools import product
from typing import List, Dict, Tuple

from crispy_forms.layout import Fieldset, Row
from django import forms
from django.utils.translation import ugettext as _

from agir.lib.form_components import *
from agir.people.person_forms.fields import is_actual_model_field, get_form_field


class FieldSet:
    def __init__(
        self, title: str, fields: List[Dict], intro_html: str = None, **kwargs
    ):
        self.title = title
        self.fields = fields
        self.intro_html = intro_html

    def set_up_fields(self, form, is_edition):
        for field_descriptor in self.fields:
            if is_actual_model_field(field_descriptor):
                # by default person fields are required
                form.fields[field_descriptor["id"]].required = field_descriptor.get(
                    "required", True
                )
                if is_edition:
                    form.fields[
                        field_descriptor["id"]
                    ].disabled = not field_descriptor.get("editable", False)

                if field_descriptor["id"] == "date_of_birth":
                    form.fields[field_descriptor["id"]].help_text = _(
                        "Format JJ/MM/AAAA"
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


class CrossTable:
    def __init__(
        self,
        *,
        title,
        intro=None,
        field,
        rows=None,
        columns=None,
        subset=None,
        **kwargs,
    ):
        self.title = title
        self.intro = intro
        self.field_descriptor = field
        self.rows = rows
        self.columns = columns
        self.subset = subset

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
        return f"<tr><th></th><th>" + "</th><th>".join(self.columns) + "</th></tr>"

    def get_row(self, form, row):
        return (
            f"<tr><th>{row}</th><td>"
            + "</td><td>".join(
                str(form[self.get_id(row, col)])
                if self.subset is None or (row, col) in self.subset
                else ""
                for col in self.columns
            )
            + "</td></tr>"
        )

    def set_up_fields(self, form: forms.Form, is_edition):
        it = self.subset or product(self.rows, self.columns)

        for (row, col) in it:
            id = self.get_id(row, col)
            field_descriptor = {**self.field_descriptor, "id": id}
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
            + "".join(self.get_row(form, row) for row in self.rows)
            + """
        </tbody>
        </table>
        """
        )

        form.helper.layout.append(Fieldset(self.title, HTML(text)))

    def collect_results(self, cleaned_data):
        it = self.subset or product(self.rows, self.columns)
        return {
            self.get_id(row, col): cleaned_data[self.get_id(row, col)]
            for row, col in it
        }


class DoubleEntryTable:
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
