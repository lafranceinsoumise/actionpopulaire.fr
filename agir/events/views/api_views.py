from datetime import timedelta

from django.db import transaction, IntegrityError
from django.db.models import Q, Value, CharField
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from agir.events.actions.rsvps import (
    rsvp_to_free_event,
    is_participant,
    cancel_rsvp_and_payment,
    RSVPException,
)
from agir.events.models import Event, GroupAttendee, OrganizerConfig, Invitation
from agir.events.models import RSVP
from agir.events.serializers import (
    EventSerializer,
    EventAdvancedSerializer,
    EventListSerializer,
    EventPropertyOptionsSerializer,
    UpdateEventSerializer,
    CreateEventSerializer,
    EventProjectSerializer,
    EventProjectDocumentSerializer,
    EventProjectListItemSerializer,
    EventReportPersonFormSerializer,
)
from agir.groups.models import SupportGroup, Membership
from agir.msgs.actions import get_viewables_messages
from agir.msgs.serializers import SupportGroupMessageSerializer
from agir.people.models import Person
from agir.people.person_forms.models import PersonForm

__all__ = [
    "EventAPIView",
    "EventDetailAPIView",
    "EventDetailAdvancedAPIView",
    "EventRsvpedAPIView",
    "PastRsvpedEventAPIView",
    "OngoingRsvpedEventsAPIView",
    "EventSuggestionsAPIView",
    "UserGroupEventAPIView",
    "GroupUpcomingEventListAPIView",
    "OrganizedEventAPIView",
    "GrandEventAPIView",
    "EventCreateOptionsAPIView",
    "CreateEventAPIView",
    "UpdateEventAPIView",
    "RSVPEventAPIView",
    "RSVPEventAsGroupAPIView",
    "EventProjectAPIView",
    "CreateEventProjectDocumentAPIView",
    "EventProjectsAPIView",
    "CreateOrganizerConfigAPIView",
    "EventGroupsOrganizersAPIView",
    "CancelEventAPIView",
    "EventReportPersonFormAPIView",
    "EventMessagesAPIView",
    "EventAssetListAPIView",
]

from agir.gestion.models import Projet

from agir.lib.rest_framework_permissions import (
    GlobalOrObjectPermissions,
    HasSpecificPermissions,
    IsPersonPermission,
    IsActionPopulaireClientPermission,
)

from agir.lib.tasks import geocode_person
from ..filters import EventFilter, GroupEventAPIFilter
from ..tasks import (
    send_cancellation_notification,
    send_group_coorganization_invitation_notification,
    send_group_attendee_notification,
)
from ...event_requests.serializers import EventAssetSerializer
from ...groups.tasks import send_new_group_event_email, notify_new_group_event
from ...lib.models import LocationMixin


class EventAPIView(RetrieveAPIView):
    permission_classes = (IsPersonPermission,)
    serializer_class = EventListSerializer
    queryset = Event.objects.public()

    def get_queryset(self):
        return self.queryset.with_serializer_prefetch(
            self.request.user.person
        ).select_related("subtype")

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
            **kwargs,
        )


class EventListAPIView(ListAPIView):
    permission_classes = (IsPersonPermission,)
    serializer_class = EventListSerializer
    queryset = Event.objects.public()
    max_length = None

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_serializer_prefetch(self.request.user.person)
            .select_related("subtype")
        )

    def filter_queryset(self, queryset):
        if self.max_length:
            return super().filter_queryset(queryset)[: self.max_length]

        return super().filter_queryset(queryset)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
            **kwargs,
        )


class EventRsvpedAPIView(EventListAPIView):
    def get(self, request, *args, **kwargs):
        person = request.user.person

        if (
            not person.coordinates
            or not person.coordinates_type
            or person.coordinates_type >= LocationMixin.COORDINATES_NO_POSITION
        ):
            geocode_person.delay(person.pk)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .listed()
            .upcoming()
            .attended_by_person(self.request.user.person)
            .order_by("start_time", "end_time")
            .distinct()
        )


class PastRsvpedEventAPIView(EventListAPIView):
    max_length = 20

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .listed()
            .past()
            .attended_by_person(self.request.user.person)
            .order_by("-end_time", "-start_time")
            .distinct()
        )


class OngoingRsvpedEventsAPIView(EventListAPIView):
    def get_queryset(self):
        now = timezone.now()
        return (
            super()
            .get_queryset()
            .listed()
            .attended_by_person(self.request.user.person)
            .filter(start_time__lte=now, end_time__gte=now)
            .order_by("start_time", "end_time")
            .distinct()
        )


# Get 20 upcoming suggestions of events : 10 national + 10 groups participants + rest near location
class EventSuggestionsAPIView(EventListAPIView):
    def get_queryset(self):
        person = self.request.user.person

        events = (
            Event.objects.with_serializer_prefetch(person)
            .select_related("subtype", "suggestion_segment")
            .listed()
            .upcoming()
        )
        national = events.national()
        near = events.none()
        national_pks = national.values_list("pk", flat=True)

        person_groups = person.supportgroups.all()
        from_groups_attendees = (
            Event.objects.public()
            .upcoming()
            .filter(
                Q(organizers_groups__in=person_groups)
                | Q(groups_attendees__in=person_groups)
            )
            .exclude(pk__in=national_pks)
            .distinct()
            .order_by("start_time")
        )[:10]
        from_groups_attendees_pks = from_groups_attendees.values_list("pk", flat=True)

        if person.coordinates is not None:
            national = national.near(coordinates=person.coordinates, radius=100)
            near = (
                events.exclude(pk__in=national_pks)
                .exclude(pk__in=from_groups_attendees_pks)
                .filter(start_time__lt=timezone.now() + timedelta(days=30))
                .near(coordinates=person.coordinates, radius=person.action_radius)
                .order_by("distance")
            )[: (10 - len(from_groups_attendees_pks))]

        near_pks = near.values_list("pk", flat=True)

        national = national[:10]

        segmented = (
            events.exclude(pk__in=national_pks)
            .exclude(pk__in=near_pks)
            .exclude(pk__in=from_groups_attendees_pks)
            .exclude(pk__in=events.grand().values_list("pk", flat=True))
            .for_segment_subscriber(person)
        )

        return sorted(
            list(segmented) + list(national) + list(from_groups_attendees) + list(near),
            key=lambda event: event.start_time,
        )


class UserGroupEventAPIView(EventListAPIView):
    def get_queryset(self):
        person = self.request.user.person
        person_groups = person.supportgroups.all()

        return (
            Event.objects.public()
            .with_serializer_prefetch(person)
            .upcoming()
            .filter(
                Q(organizers_groups__in=person_groups)
                | Q(groups_attendees__in=person_groups)
            )
            .distinct()
            .order_by("start_time")
        )


class GroupUpcomingEventListAPIView(EventListAPIView):
    queryset = Event.objects.listed()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupEventAPIFilter
    max_length = 200

    def get_queryset(self):
        return super().get_queryset().upcoming().distinct().order_by("start_time")


class OrganizedEventAPIView(EventListAPIView):
    queryset = Event.objects.exclude(visibility=Event.VISIBILITY_ADMIN)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter
    max_length = 10

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .organized_by_person(self.request.user.person)
            .distinct()
            .order_by("-start_time")
        )


class GrandEventAPIView(EventListAPIView):
    def get_queryset(self):
        return (
            Event.objects.with_serializer_prefetch(self.request.user.person)
            .listed()
            .upcoming()
            .grand()
            .order_by("start_time")
        )


class EventCreateOptionsAPIView(RetrieveAPIView):
    permission_classes = (IsPersonPermission,)
    serializer_class = EventPropertyOptionsSerializer
    queryset = Event.objects.all()

    def get_object(self):
        return self.request


class CreateEventPermissions(HasSpecificPermissions):
    permissions = ["events.add_event"]


class CreateEventAPIView(CreateAPIView):
    permission_classes = (
        IsPersonPermission,
        CreateEventPermissions,
    )
    serializer_class = CreateEventSerializer
    queryset = Event.objects.all()


class EventManagementPermissions(GlobalOrObjectPermissions):
    message = (
        "Vous n'avez pas la permission d'effectuer cette action."
        "Veuillez contacter nos équipes à groupes@actionpopulaire.fr"
    )

    perms_map = {
        "GET": [],
        "POST": [],
        "PUT": [],
        "PATCH": [],
        "DELETE": [],
    }
    object_perms_map = {
        "GET": ["events.view_event_settings"],
        "POST": ["events.change_event"],
        "PUT": ["events.change_event"],
        "PATCH": ["events.change_event"],
        "DELETE": ["events.delete_event"],
    }


class EventViewPermissions(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
    }
    object_perms_map = {
        "GET": ["events.view_event"],
    }


class EventDetailAPIView(RetrieveAPIView):
    permission_classes = (
        IsActionPopulaireClientPermission,
        EventViewPermissions,
    )
    serializer_class = EventSerializer
    queryset = Event.objects.exclude(visibility=Event.VISIBILITY_ADMIN)

    def get_queryset(self):
        person = (None,)
        if not self.request.user.is_anonymous and hasattr(self.request.user, "person"):
            person = self.request.user.person

        return super().get_queryset().with_serializer_prefetch(person)


class EventDetailAdvancedAPIView(RetrieveAPIView):
    permission_classes = (
        IsPersonPermission,
        EventManagementPermissions,
    )
    serializer_class = EventAdvancedSerializer
    queryset = Event.objects.exclude(visibility=Event.VISIBILITY_ADMIN)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_serializer_prefetch(person=self.request.user.person)
        )


class UpdateEventAPIView(UpdateAPIView):
    permission_classes = (
        IsPersonPermission,
        EventManagementPermissions,
    )
    queryset = Event.objects.exclude(visibility=Event.VISIBILITY_ADMIN)
    serializer_class = UpdateEventSerializer


class CreateOrganizerConfigAPIView(APIView):
    permission_classes = (
        IsPersonPermission,
        EventManagementPermissions,
    )
    queryset = OrganizerConfig.objects.all()

    def post(self, request, pk):
        organizer_id = request.data.get("organizer_id")
        event = Event.objects.get(pk=pk)
        person = Person.objects.get(pk=organizer_id)
        if len(OrganizerConfig.objects.filter(event=event, person=person)) > 0:
            raise exceptions.ValidationError(
                detail={"detail": "Cette personne est déjà organisateur·ice"},
                code="invalid_format",
            )
        organizer_config = OrganizerConfig(event=event, person=person)
        organizer_config.save()
        return JsonResponse({"data": True})


# Send group invitations to organize an event
class EventGroupsOrganizersAPIView(ListCreateAPIView):
    permission_classes = (
        IsPersonPermission,
        EventManagementPermissions,
    )
    # Restrict to public and upcoming events
    queryset = Event.objects.public().upcoming()

    # List will return the last co-organizer groups for the person's events
    def list(self, request, *args, **kwargs):
        event = self.get_object()
        recent_coorganizers = SupportGroup.objects.filter(
            pk__in=(
                OrganizerConfig.objects.exclude(as_group__isnull=True)
                .exclude(as_group__published=False)
                .exclude(event_id=event.id)
                .exclude(event__visibility=Event.VISIBILITY_ADMIN)
                .filter(
                    Q(person_id=request.user.person.id)
                    | Q(
                        as_group_id__in=event.organizers_groups.values_list(
                            "id", flat=True
                        )
                    )
                )
                .distinct("as_group_id")
                .order_by("as_group_id", "-event__end_time")
                .values_list("as_group_id", flat=True)[:10]
            )
        )

        return Response(
            [
                {
                    "id": group.id,
                    "name": group.name,
                    "type": group.get_type_display(),
                    "location": {
                        "city": group.location_city,
                        "zip": group.location_zip,
                    },
                }
                for group in recent_coorganizers
            ]
        )

    def create(self, request, *args, **kwargs):
        # Use pk in URL to retrieve the event, returns 404 if not found,
        # check the permissions if found
        event = self.get_object()
        # Retrieve group by id or return a 404 response
        group = get_object_or_404(
            SupportGroup.objects.active(), pk=request.data.get("groupPk")
        )
        member = self.request.user.person

        # Check if group is already organizing the event
        if not event.subtype.is_coorganizable:
            raise exceptions.PermissionDenied(
                detail={
                    "detail": "La coorganisation n'est pas autorisée pour ce type d'événement"
                },
            )

        # Check if group is already organizing the event
        if OrganizerConfig.objects.filter(event=event, as_group=group).exists():
            raise exceptions.ValidationError(
                detail={"detail": "Ce groupe coorganise déjà l'événement"},
                code="invalid_format",
            )

        # Create organizer config if current person is the group referent
        if member in group.referents:
            OrganizerConfig.objects.create(
                event=event,
                person=member,
                as_group=group,
            )
            # Notify the group members
            send_new_group_event_email.delay(group.id, event.id)
            notify_new_group_event.delay(group.id, event.id)

            return Response(status=status.HTTP_201_CREATED)

        # Send a coorganization invitation otherwise
        with transaction.atomic():
            (invitation, created) = Invitation.objects.get_or_create(
                event=event,
                group=group,
                defaults={"person_sender": member, "status": Invitation.STATUS_PENDING},
            )

            if not created:
                invitation.person_sender = member
                invitation.person_recipient = None
                invitation.status = Invitation.STATUS_PENDING
                invitation.save()

            send_group_coorganization_invitation_notification.delay(invitation.pk)

            return Response(status=status.HTTP_202_ACCEPTED)


class CancelEventAPIView(DestroyAPIView):
    permission_classes = (
        IsPersonPermission,
        EventManagementPermissions,
    )
    queryset = Event.objects.public().upcoming(
        as_of=timezone.now(), published_only=False
    )

    def perform_destroy(self, event):
        event.visibility = Event.VISIBILITY_ADMIN
        event.save()
        send_cancellation_notification.delay(event.pk)


class RSVPEventPermissions(GlobalOrObjectPermissions):
    perms_map = {"POST": [], "DELETE": []}
    object_perms_map = {
        "POST": ["events.create_rsvp_for_event"],
        "DELETE": ["events.cancel_rsvp_for_event"],
    }


class RSVPEventAPIView(DestroyAPIView, CreateAPIView):
    queryset = Event.objects.public()
    permission_classes = (
        IsPersonPermission,
        RSVPEventPermissions,
    )

    @cached_property
    def user_is_already_rsvped(self):
        return is_participant(self.event, self.request.user.person)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.person = self.request.user.person
        self.event = self.get_object()

    def create(self, request, *args, **kwargs):
        if self.event.is_past() or self.user_is_already_rsvped:
            raise PermissionDenied(
                detail={
                    "redirectTo": self.event.get_absolute_url(),
                },
            )
        if bool(self.event.subscription_form_id):
            raise PermissionDenied(
                detail={
                    "redirectTo": reverse("rsvp_event", kwargs={"pk": self.event.pk})
                },
            )
        if not self.event.is_free:
            if "rsvp_submission" in request.session:
                del request.session["rsvp_submission"]

            request.session["rsvp_event"] = str(self.event.pk)
            request.session["is_guest"] = False

            raise PermissionDenied(
                detail={"redirectTo": reverse("pay_event")},
            )

        try:
            rsvp_to_free_event(self.event, self.person)
        except RSVPException as e:
            raise PermissionDenied(detail=str(e))

        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            rsvp = RSVP.objects.get(person=self.person, event=self.event)
        except RSVP.DoesNotExist:
            rsvp = RSVP(person=self.person, event=self.event)

        try:
            cancel_rsvp_and_payment(rsvp, self.person)
        except RSVPException as e:
            raise PermissionDenied(str(e))

        return Response(status=status.HTTP_204_NO_CONTENT)


class RSVPEventAsGroupPermissions(GlobalOrObjectPermissions):
    perms_map = {"POST": [], "DELETE": []}
    object_perms_map = {
        "POST": ["events.rsvp_event_as_group"],
        "DELETE": ["events.rsvp_event_as_group"],
    }


class RSVPEventAsGroupAPIView(CreateAPIView, DestroyAPIView):
    queryset = Event.objects.public()
    group_queryset = SupportGroup.objects.active()
    permission_classes = (
        IsPersonPermission,
        RSVPEventAsGroupPermissions,
    )

    def check_group_permissions(self, group):
        if not self.person.memberships.managers().filter(supportgroup=group).exists():
            raise PermissionDenied(
                detail={
                    "detail": "Vous n'avez pas le rôle requis pour faire rejoindre ce groupe à l'événement"
                },
            )

    def get_group(self):
        queryset = self.group_queryset
        group = get_object_or_404(queryset, pk=self.kwargs["group_pk"])
        self.check_group_permissions(group)

        return group

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.person = request.user.person
        self.event = self.get_object()
        self.group = self.get_group()

    def create(self, request, *args, **kwargs):
        if self.event.is_past():
            raise exceptions.ValidationError(
                detail={
                    "detail": "Il n'est pas possible de participer à cet événement car il est déjà terminé !"
                },
                code="invalid_format",
            )
        if self.event.organizers_groups.filter(pk=self.group.pk).exists():
            raise exceptions.ValidationError(
                detail={"detail": "Ce groupe organise déjà l'événement !"},
                code="invalid_format",
            )

        try:
            group_attendee = GroupAttendee.objects.create(
                event=self.event, group=self.group, organizer=self.person
            )
        except IntegrityError:
            raise exceptions.ValidationError(
                detail={"detail": "Ce groupe participe déjà à l'événement !"},
                code="invalid_format",
            )

        send_group_attendee_notification.delay(group_attendee.pk)

        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        group_attendee = get_object_or_404(
            GroupAttendee.objects.all(), group=self.group, event=self.event
        )
        group_attendee.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class EventAssetsPermissions(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
    }
    object_perms_map = {
        "GET": ["events.view_event_settings"],
    }


class EventAssetListAPIView(ListAPIView):
    permission_classes = (IsPersonPermission, EventAssetsPermissions)
    queryset = Event.objects.exclude(visibility=Event.VISIBILITY_ADMIN)
    serializer_class = EventAssetSerializer

    def list(self, request, *args, **kwargs):
        event = self.get_object()
        queryset = event.event_assets.public()
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EventProjectPermission(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "PUT": [], "PATCH": []}
    object_perms_map = {
        "GET": ["events.view_event_settings"],
        "PUT": ["events.upload_event_documents"],
        "PATCH": ["events.upload_event_documents"],
    }


class EventProjectsAPIView(ListAPIView):
    permission_classes = (IsPersonPermission,)
    serializer_class = EventProjectListItemSerializer
    queryset = Projet.objects.filter(event__isnull=False)

    # Get projects from events user organize or is manager from group organizer
    def get_queryset(self):
        person = self.request.user.person

        as_manager_events = (
            OrganizerConfig.objects.filter(
                Q(person=person)
                | Q(
                    as_group_id__in=Membership.objects.filter(
                        person=person,
                        membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
                    ).values_list("supportgroup_id", flat=True)
                )
            )
            .distinct("pk")
            .exclude(event__visibility=Event.VISIBILITY_ADMIN)
            .values_list("event_id", flat=True)
        )

        if len(as_manager_events) == 0:
            return self.queryset.none()

        return (
            self.queryset.filter(event__in=as_manager_events)
            .select_related("event", "event__subtype")
            .order_by("event__end_time")
        )


class EventProjectAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        IsPersonPermission,
        EventProjectPermission,
    )
    serializer_class = EventProjectSerializer
    queryset = (
        Projet.objects.filter(event__isnull=False)
        .exclude(event__visibility=Event.VISIBILITY_ADMIN)
        .select_related("event", "event__subtype")
    )
    lookup_field = "event_id"

    def check_object_permissions(self, request, obj):
        return super().check_object_permissions(request, obj.event)


class CreateEventProjectDocumentPermission(GlobalOrObjectPermissions):
    perms_map = {
        "POST": [],
    }
    object_perms_map = {
        "POST": ["events.upload_event_documents"],
    }


class CreateEventProjectDocumentAPIView(CreateAPIView):
    permission_classes = (
        IsPersonPermission,
        CreateEventProjectDocumentPermission,
    )
    serializer_class = EventProjectDocumentSerializer
    queryset = Projet.objects.filter(event__isnull=False)
    lookup_field = "event_id"

    def check_object_permissions(self, request, obj):
        return super().check_object_permissions(request, obj.event)

    def perform_create(self, serializer):
        project = self.get_object()
        with transaction.atomic():
            document = serializer.save()
            project.documents.add(document)


class EventReportPersonFormPermission(GlobalOrObjectPermissions):
    perms_map = {"GET": []}
    object_perms_map = {
        "GET": ["events.view_event_settings"],
    }


class EventReportPersonFormAPIView(RetrieveAPIView):
    permission_classes = (
        IsPersonPermission,
        EventReportPersonFormPermission,
    )
    serializer_class = EventReportPersonFormSerializer

    def get_queryset(self):
        limit_date = timezone.now() - timezone.timedelta(days=7)
        return Event.objects.public().filter(end_time__gte=limit_date)

    def get_object(self):
        event = super().get_object()
        queryset = PersonForm.objects.published().annotate(
            event_pk=Value(event.pk, output_field=CharField())
        )
        return get_object_or_404(queryset, event_subtype=event.subtype)


class EventMessagesAPIView(ListAPIView):
    serializer_class = SupportGroupMessageSerializer
    permission_classes = (IsPersonPermission,)

    def initial(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=kwargs["pk"])
        except Event.DoesNotExist:
            raise NotFound()

        super().initial(request, *args, **kwargs)
        self.check_object_permissions(request, self.event)

    def get_queryset(self):
        person = self.request.user.person

        return (
            get_viewables_messages(person)
            .filter(linked_event=self.event)
            .order_by("-created")
        )
