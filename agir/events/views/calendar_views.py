import ics
from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView

from agir.events.models import Calendar, Event, EventSubtype
from agir.front.view_mixins import ObjectOpengraphMixin
from agir.lib.views import IframableMixin


class CalendarView(IframableMixin, ObjectOpengraphMixin, ListView):
    model = Calendar
    paginate_by = 10
    context_object_name = "events"

    def get_template_names(self):
        if self.request.GET.get("iframe"):
            return ["events/calendar_iframe.html"]
        return ["events/calendar.html"]

    def get(self, request, *args, **kwargs):
        try:
            self.calendar = self.object = self.model.objects.get(
                slug=self.kwargs.get("slug")
            )
        except self.model.DoesNotExist:
            raise Http404("Ce calendrier n'existe pas.")

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        calendar_ids = self.get_calendar_ids(self.calendar.id)

        return (
            Event.objects.upcoming(as_of=timezone.now())
            .filter(calendar_items__calendar_id__in=calendar_ids)
            .order_by("start_time", "id")
            .distinct("start_time", "id")
        )

    def get_context_data(self, **kwargs):
        # get all ids of calendar that are either the one selected, or children of it
        return super().get_context_data(
            default_event_image=settings.DEFAULT_EVENT_IMAGE, calendar=self.calendar
        )

    @staticmethod
    def get_calendar_ids(parent_id):
        ids = Calendar.objects.raw(
            """
        WITH RECURSIVE children AS (
            SELECT id
            FROM events_calendar
            WHERE id = %s
          UNION ALL
            SELECT c.id
            FROM events_calendar AS c
            JOIN children
            ON c.parent_id = children.id
        )
        SELECT id FROM children;
        """,
            [parent_id],
        )

        return list(ids)


class CalendarIcsView(DetailView):
    model = Calendar

    def render_to_response(self, context, **response_kwargs):
        calendar = ics.Calendar(
            events=[
                event.to_ics()
                for event in self.object.events.filter(
                    visibility=Event.VISIBILITY_PUBLIC
                )
            ]
        ).serialize()

        return HttpResponse(calendar, content_type="text/calendar")


class EventSubtypeIcsView(CalendarIcsView):
    model = EventSubtype
    queryset = EventSubtype.objects.exclude(visibility=EventSubtype.VISIBILITY_NONE)
