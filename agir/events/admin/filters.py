import django_filters
from django.contrib.admin.widgets import AutocompleteSelect
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django_filters import filters

from agir.events.models import Calendar, EventSubtype, Event
from agir.lib.autocomplete_filter import AutocompleteRelatedModelFilter


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


class RelatedEventFilter(AutocompleteRelatedModelFilter):
    title = "événement"
    parameter_name = "event"

    def get_rendered_widget(self):
        rel = models.ForeignKey(to=Event, on_delete=models.CASCADE)
        rel.model = Event
        widget = AutocompleteSelect(
            rel,
            self.model_admin.admin_site,
        )
        FieldClass = self.get_form_field()
        field = FieldClass(
            queryset=self.get_queryset_for_field(),
            widget=widget,
            required=False,
        )
        self._add_media(self.model_admin, widget)

        attrs = self.widget_attrs.copy()
        attrs["id"] = "id-%s-autocomplete-filter" % self.field_name
        attrs["class"] = f'{attrs.get("class", "")} select-filter'.strip()

        return field.widget.render(
            name=self.parameter_name,
            value=self.used_parameters.get(self.parameter_name, ""),
            attrs=attrs,
        ) + format_html(
            '<a style="margin-top: 5px" href="{}">Gérer les événements</a>',
            reverse("admin:events_event_changelist"),
        )

    def get_queryset_for_field(self):
        return Event.objects.all()

    def queryset(self, request, queryset):
        if self.value():
            try:
                event = Event.objects.get(pk=self.value())
                return queryset.filter(event_id=event.pk)
            except Event.DoesNotExist:
                pass

        return queryset
