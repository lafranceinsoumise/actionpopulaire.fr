import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Submit, Div
from django import forms

from agir.events.models import EventSubtype, Event, EventTag
from agir.lib.filters import FixedModelMultipleChoiceFilter


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

    class Meta:
        model = Event
        fields = []
        form = EventFilterForm


class EventAPIFilter(EventFilter, django_filters.rest_framework.FilterSet):
    pass
