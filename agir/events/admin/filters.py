import django_filters
from django_filters import filters

from agir.events.models import Calendar, EventSubtype, Event


class EventFilterSet(django_filters.FilterSet):
    calendars = filters.ModelMultipleChoiceFilter(
        field_name="calendars", queryset=Calendar.objects.all(), label="Calendriers"
    )
    date = filters.DateFromToRangeFilter(
        field_name="start_time", lookup_expr="range", label="Entre les dates"
    )
    subtype = django_filters.filterset.ModelMultipleChoiceFilter(
        queryset=EventSubtype.objects.all()
    )

    class Meta:
        model = Event
        fields = ["visibility"]
