from datetime import timedelta

import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Submit, Div
from data_france.models import CodePostal
from django import forms
from django.utils import timezone

from agir.events.models import EventSubtype, Event, EventTag
from agir.groups.models import SupportGroup
from agir.lib.data import departements_choices, filtre_departement
from agir.lib.filters import FixedModelMultipleChoiceFilter, ModelChoiceInFilter


class EventFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Row(Div("q", css_class="col-md-8"), Div("type", css_class="col-md-4")),
            "past",
        )
        self.helper.add_input(Submit("chercher", "Chercher"))


class EventFilter(django_filters.rest_framework.FilterSet):
    q = django_filters.CharFilter(method="filter_search", label="Chercher")

    type = django_filters.ChoiceFilter(
        field_name="subtype__type",
        lookup_expr="exact",
        label="Type d'événement",
        choices=EventSubtype.TYPE_CHOICES,
    )

    subtype = FixedModelMultipleChoiceFilter(
        field_name="subtype",
        to_field_name="label",
        queryset=EventSubtype.objects.all(),
    )

    include_past = django_filters.BooleanFilter(
        label="Inclure les événements passés",
        method="filter_include_past",
        widget=forms.CheckboxInput(),
    )

    tag = FixedModelMultipleChoiceFilter(
        field_name="tags",
        to_field_name="label",
        queryset=EventTag.objects.all(),
    )

    date = django_filters.DateFilter(
        label="Date", method="filter_by_date", widget=forms.DateInput
    )

    group = django_filters.UUIDFilter(
        method="filter_group", label="Groupe organisateur"
    )

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()
            if data.get("include_past") is None:
                data["include_past"] = False
            if data.get("include_hidden") is None:
                data["include_hidden"] = False

        super().__init__(data, *args, **kwargs)

    def filter_include_past(self, qs, name, value):
        if not value:
            return qs.upcoming(published_only=False)
        else:
            return qs

    def filter_by_date(self, qs, name, value):
        if value:
            return qs.filter(start_time__date__lte=value, end_time__date__gte=value)
        else:
            return qs

    def filter_search(self, qs, name, terms):
        if terms:
            return qs.search(terms)
        return qs

    def filter_group(self, qs, name, group):
        if group:
            return qs.filter(organizers_groups__id=group)
        return qs

    class Meta:
        model = Event
        fields = []
        form = EventFilterForm


class EventAPIFilter(EventFilter, django_filters.rest_framework.FilterSet):
    pass


class GroupEventAPIFilter(django_filters.rest_framework.FilterSet):
    timing = django_filters.ChoiceFilter(
        method="filter_timing",
        choices=(("week", "Cette semaine"), ("month", "Ce mois-ci")),
        initial="week",
    )
    zip = django_filters.ChoiceFilter(
        field_name="location_zip",
        choices=lambda: tuple(
            (code, code)
            for code in CodePostal.objects.all().values_list("code", flat=True)
        ),
    )
    departement = django_filters.ChoiceFilter(
        method="filter_departement",
        choices=departements_choices,
    )
    groups = ModelChoiceInFilter(
        field_name="organizers_groups",
        lookup_expr="in",
        to_field_name="id",
        queryset=SupportGroup.objects.active(),
        distinct=True,
    )

    def __init__(self, data=None, *args, **kwargs):
        # if filterset is bound, use initial values as defaults
        if data is not None:
            # get a mutable copy of the QueryDict
            data = data.copy()

            for name, f in self.base_filters.items():
                initial = f.extra.get("initial")

                # filter param is either missing or empty, use initial as default
                if not data.get(name) and initial:
                    data[name] = initial

        super().__init__(data, *args, **kwargs)

    @property
    def qs(self):
        # noinspection PyStatementEffect
        self.errors

        # At least two filtering parameters should be given
        if len([value for value in self.form.cleaned_data.values() if value]) > 1:
            return super().qs

        return self.queryset.none()

    def filter_timing(self, qs, name, value):
        if value not in ("week", "month"):
            value = "week"

        today = timezone.now().date()
        current_week_monday = today - timedelta(days=today.weekday())

        if value == "week" and today.weekday() < 5:
            current_week_sunday = current_week_monday + timedelta(days=6)

            return qs.filter(
                start_time__date__gte=current_week_monday,
                start_time__date__lte=current_week_sunday,
            )

        if value == "week":
            next_week_monday = current_week_monday + timedelta(days=7)
            next_week_sunday = next_week_monday + timedelta(days=6)

            return qs.filter(
                start_time__date__gte=today,
                start_time__date__lte=next_week_sunday,
            )

        if value == "month":
            return qs.filter(
                start_time__date__gte=today,
                start_time__month=today.month,
                start_time__year=today.year,
            )

        return qs

    def filter_departement(self, qs, name, value):
        if not value:
            return qs

        return qs.filter(filtre_departement(value))

    class Meta:
        model = Event
        fields = ["timing", "zip", "departement", "groups"]
