import django_filters
from django_filters import filters

from agir.events.models import Calendar, EventSubtype


class EventFilterSet(django_filters.FilterSet):
    published = filters.BooleanFilter("published")
    calendars = filters.ModelMultipleChoiceFilter(
        field_name="calendars", queryset=Calendar.objects.all(), label="Calendriers"
    )
    date = filters.DateFromToRangeFilter(
        field_name="start_time", lookup_expr="range", label="Entre les dates"
    )
    subtype = django_filters.filterset.ModelMultipleChoiceFilter(
        queryset=EventSubtype.objects.all()
    )
