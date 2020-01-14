import django_filters

from agir.lib.filters import FixedModelMultipleChoiceFilter, DistanceFilter
from agir.events.models import EventSubtype, Event, Calendar


class EventFilterSet(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Chercher")

    subtype = FixedModelMultipleChoiceFilter(
        field_name="subtype", to_field_name="label", queryset=EventSubtype.objects.all()
    )
    include_past = django_filters.BooleanFilter(
        label="Inclure les événements passés", method="filter_include_past"
    )
    before = django_filters.DateFilter(
        field_name="end_time", lookup_expr="date__gte", label="Avant la date"
    )
    after = django_filters.DateFilter(
        field_name="start_time", lookup_expr="date__lte", label="Après la date"
    )

    calendar = django_filters.ModelChoiceFilter(
        field_name="calendars", to_field_name="slug", queryset=Calendar.objects.all()
    )

    distance = DistanceFilter(field_name="coordinates", label="Près de")

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()
            if data.get("include_past") is None:
                data["include_past"] = False
            if data.get("include_hidden") is None:
                data["include_hidden"] = False

        super().__init__(data, *args, **kwargs)

    @property
    def qs(self):
        return super().qs[:5000]

    def filter_include_past(self, queryset, name, value):
        if not value:
            return queryset.upcoming(published_only=False)
        else:
            return queryset

    def filter_include_hidden(self, qs, name, value):
        if not value:
            return qs.listed()
        else:
            return qs

    def filter_search(self, qs, terms):
        if terms:
            return qs.search(terms)
        return qs

    class Meta:
        model = Event
        fields = ("subtype", "include_past")


class EventAPIFilterSet(EventFilterSet, django_filters.rest_framework.FilterSet):
    pass
