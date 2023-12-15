import urllib.parse

import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Div, Submit
from data_france.models import CodePostal
from django import forms
from django.forms import CheckboxInput

from agir.groups.models import SupportGroup
from agir.lib.data import departements_choices, filtre_departements
from agir.lib.filters import DistanceFilter, ChoiceInFilter


class GroupFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Row(Div("q", css_class="col-md-8"), Div("type", css_class="col-md-4")),
            "certified",
        )
        self.helper.add_input(Submit("chercher", "Chercher"))


class GroupFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search", label="Chercher")

    type = django_filters.ChoiceFilter(
        field_name="type", label="Limiter au type", choices=SupportGroup.TYPE_CHOICES
    )

    distance = DistanceFilter(field_name="coordinates", label="Près de")

    certified = django_filters.BooleanFilter(
        method="filter_certified",
        label="Groupes certifiés uniquement",
        widget=CheckboxInput,
    )

    def filter_search(self, qs, name, terms):
        if terms:
            terms = urllib.parse.unquote(terms)
            return qs.search(terms)
        return qs

    def filter_certified(self, qs, name, value):
        if value is True:
            return qs.certified()
        return qs

    @property
    def qs(self):
        # noinspection PyStatementEffect
        self.errors
        if self.form.cleaned_data.get("q"):
            return super().qs
        return self.queryset.none()

    class Meta:
        model = SupportGroup
        fields = []
        form = GroupFilterForm


class GroupAPIFilterSet(GroupFilterSet, django_filters.rest_framework.FilterSet):
    exclude = django_filters.CharFilter(
        method="filter_exclude",
        label="Sauf l'id de groupe",
    )

    def filter_exclude(self, qs, name, value):
        return qs.exclude(pk__in=[value])


class GroupLocationAPIFilterSet(django_filters.rest_framework.FilterSet):
    type = django_filters.ChoiceFilter(
        field_name="type", label="Limiter au type", choices=SupportGroup.TYPE_CHOICES
    )

    zip = ChoiceInFilter(
        field_name="location_zip",
        lookup_expr="in",
        label="Limiter aux codes postaux",
        choices=lambda: tuple(
            (code, code)
            for code in CodePostal.objects.all().values_list("code", flat=True)
        ),
    )

    departement = ChoiceInFilter(
        method="filter_departement",
        label="Limiter au departement",
        choices=departements_choices,
    )

    def filter_departement(self, qs, name, value):
        if not value:
            return qs

        values = value if isinstance(value, list) else [value]

        return qs.filter(filtre_departements(*values))

    @property
    def qs(self):
        # noinspection PyStatementEffect
        self.errors

        if any(self.form.cleaned_data.values()):
            return super().qs

        return self.queryset.none()

    class Meta:
        model = SupportGroup
        fields = []
        form = GroupFilterForm
