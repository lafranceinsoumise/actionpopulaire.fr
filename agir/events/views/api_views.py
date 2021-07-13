from datetime import timedelta

from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.exceptions import NotFound, MethodNotAllowed, PermissionDenied
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.events.actions.rsvps import (
    rsvp_to_free_event,
    is_participant,
)
from agir.events.models import Event
from agir.events.models import RSVP
from agir.events.serializers import (
    EventSerializer,
    EventListSerializer,
    EventPropertyOptionsSerializer,
    UpdateEventSerializer,
    CreateEventSerializer,
    EventProjectSerializer,
)

__all__ = [
    "EventDetailAPIView",
    "EventRsvpedAPIView",
    "EventSuggestionsAPIView",
    "EventCreateOptionsAPIView",
    "CreateEventAPIView",
    "UpdateEventAPIView",
    "RSVPEventAPIView",
    "EventProjectAPIView",
]

from agir.gestion.models import Projet

from agir.lib.rest_framework_permissions import GlobalOrObjectPermissions

from agir.lib.tasks import geocode_person


class EventRsvpedAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EventListSerializer

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=EventListSerializer.EVENT_CARD_FIELDS, **kwargs,
        )

    def get(self, request, *args, **kwargs):
        person = request.user.person

        if person.coordinates_type is None:
            geocode_person.delay(person.pk)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        person = self.request.user.person
        queryset = Event.objects.public().with_serializer_prefetch(person)

        return (
            (
                queryset.upcoming()
                .filter(Q(attendees=person) | Q(organizers=person))
                .order_by("start_time", "end_time")
            )
            .distinct()
            .select_related("subtype")
        )


class EventDetailAPIView(RetrieveAPIView):
    permission_ = ("events.view_event",)
    serializer_class = EventSerializer
    queryset = Event.objects.all()


class EventSuggestionsAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EventListSerializer

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=EventListSerializer.EVENT_CARD_FIELDS, **kwargs,
        )

    def get_queryset(self):
        person = self.request.user.person
        person_groups = person.supportgroups.all()
        base_queryset = Event.objects.with_serializer_prefetch(person)

        groups_events = (
            base_queryset.upcoming()
            .filter(organizers_groups__in=person_groups)
            .distinct()
        )

        organized_events = (
            base_queryset.past()
            .filter(organizers=person)
            .distinct()
            .order_by("-start_time")[:10]
        )

        past_events = (
            base_queryset.past()
            .filter(Q(rsvps__person=person) | Q(organizers_groups__in=person_groups))
            .distinct()
            .order_by("-start_time")[:10]
        )

        result = groups_events.union(organized_events, past_events)

        if person.coordinates is not None:
            near_events = (
                base_queryset.upcoming()
                .filter(
                    start_time__lt=timezone.now() + timedelta(days=30),
                    do_not_list=False,
                )
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("distance")[:10]
            )

            result = (
                base_queryset.filter(
                    pk__in=[e.pk for e in near_events] + [e.pk for e in result]
                )
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("start_time")
                .distinct()
            ).select_related("subtype")
        else:
            result = result.order_by("start_time")

        return result


class EventManagementPermissions(GlobalOrObjectPermissions):
    perms_map = {
        "OPTIONS": [],
        "GET": [],
        "POST": ["events.add_event",],
        "PUT": [],
        "PATCH": [],
    }
    object_perms_map = {
        "OPTIONS": [],
        "GET": [],
        "POST": [],
        "PUT": ["events.change_event"],
        "PATCH": ["events.change_event"],
    }


class EventCreateOptionsAPIView(RetrieveAPIView):
    permission_classes = (EventManagementPermissions,)
    serializer_class = EventPropertyOptionsSerializer
    queryset = Event.objects.all()

    def initial(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous or not user.person:
            raise PermissionDenied()
        self.person = user.person
        return super().initial(request, *args, **kwargs)

    def get_object(self):
        return self.request


class CreateEventAPIView(CreateAPIView):
    permission_classes = (EventManagementPermissions,)
    serializer_class = CreateEventSerializer
    queryset = Event.objects.all()


class UpdateEventAPIView(UpdateAPIView):
    permission_classes = (EventManagementPermissions,)
    queryset = Event.objects.all()
    serializer_class = UpdateEventSerializer


class RSVPEventPermissions(GlobalOrObjectPermissions):
    perms_map = {"POST": [], "DELETE": []}
    object_perms_map = {
        "POST": ["events.create_rsvp_for_event"],
        "DELETE": ["events.delete_rsvp_for_event"],
    }


class RSVPEventAPIView(DestroyAPIView, CreateAPIView):
    queryset = Event.objects.public()
    permission_classes = (RSVPEventPermissions,)

    @cached_property
    def user_is_already_rsvped(self):
        return is_participant(self.object, self.request.user.person)

    def initial(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.check_object_permissions(request, self.object)

        super().initial(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        rsvp_to_free_event(self.object, request.user.person)
        return Response(status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        if self.user_is_already_rsvped:
            raise MethodNotAllowed(
                "POST",
                detail={
                    "redirectTo": reverse("view_event", kwargs={"pk": self.object.pk})
                },
            )

        if bool(self.object.subscription_form_id):
            raise MethodNotAllowed(
                "POST",
                detail={
                    "redirectTo": reverse("rsvp_event", kwargs={"pk": self.object.pk})
                },
            )

        if not self.object.is_free:
            if "rsvp_submission" in request.session:
                del request.session["rsvp_submission"]
            request.session["rsvp_event"] = str(self.object.pk)
            request.session["is_guest"] = False
            raise MethodNotAllowed(
                "POST", detail={"redirectTo": reverse("pay_event")},
            )

        return super().post(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            rsvp = (
                RSVP.objects.filter(event__end_time__gte=timezone.now())
                .select_related("event")
                .get(event=self.object, person=self.request.user.person)
            )
        except RSVP.DoesNotExist:
            raise NotFound()

        rsvp.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class EventProjectPermission(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
    }
    object_perms_map = {"GET": ["events.change_event"]}


class EventProjectAPIView(RetrieveAPIView):
    permission_classes = (EventProjectPermission,)
    serializer_class = EventProjectSerializer
    queryset = (
        Projet.objects.filter(event__isnull=False)
        .select_related("event", "event__subtype")
        .prefetch_related("documents")
    )
    lookup_field = "event_id"

    def check_object_permissions(self, request, obj):
        return super().check_object_permissions(request, obj.event)
