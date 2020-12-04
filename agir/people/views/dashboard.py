from datetime import timedelta

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.core.paginator import Paginator
from django.db.models import (
    Value,
    TextField,
    Q,
    Case,
    When,
    BooleanField,
    Sum,
    Exists,
    OuterRef,
)
from django.utils import timezone
from django.views.generic import TemplateView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.events.models import Event
from agir.groups.actions import get_promo_codes
from agir.groups.actions.promo_codes import is_promo_code_delayed, next_promo_code_date
from agir.groups.models import SupportGroup, Membership
from agir.lib.tasks import geocode_person
from agir.municipales.models import CommunePage
from agir.payments.models import Payment


class DashboardView(SoftLoginRequiredMixin, TemplateView):
    template_name = "people/dashboard.html"

    def get(self, request, *args, **kwargs):
        person = request.user.person

        if person.coordinates_type is None:
            geocode_person.delay(person.pk)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        rsvped_events = (
            Event.objects.upcoming()
            .filter(attendees=person)
            .order_by("start_time", "end_time")
        )
        if person.coordinates is not None:
            rsvped_events = rsvped_events.annotate(
                distance=Distance("coordinates", person.coordinates)
            )

        members_groups = list(
            SupportGroup.objects.filter(memberships__person=person, published=True)
            .order_by("name")
            .annotate(
                user_is_manager=Exists(
                    Membership.objects.filter(
                        supportgroup_id=OuterRef("id"),
                        person=person,
                        membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
                    )
                ),
                has_promo_code=Sum(
                    Case(
                        When(tags__label=settings.PROMO_CODE_TAG, then=1),
                        default=0,
                        output_field=BooleanField(),
                    )
                ),
            )
        )

        promo_code_delay = None

        suggested_events = (
            Event.objects.upcoming()
            .exclude(rsvps__person=person)
            .filter(organizers_groups__in=person.supportgroups.all())
            .annotate(
                reason=Value(
                    "Cet événément est organisé par un groupe dont vous êtes membre.",
                    TextField(),
                )
            )
            .order_by("start_time")
        )
        if person.coordinates is not None:
            suggested_events = suggested_events.annotate(
                distance=Distance("coordinates", person.coordinates)
            )

        last_events = Paginator(
            Event.objects.past()
            .filter(Q(attendees=person) | Q())
            .order_by("-start_time", "-end_time"),
            5,
        ).get_page(self.request.GET.get("last_events_page"))

        if person.coordinates is not None and len(suggested_events) < 10:
            close_events = (
                Event.objects.upcoming()
                .filter(
                    start_time__lt=timezone.now() + timedelta(days=30),
                    do_not_list=False,
                )
                .exclude(pk__in=suggested_events)
                .exclude(rsvps__person=person)
                .annotate(
                    reason=Value(
                        "Cet événement se déroule près de chez vous.", TextField()
                    )
                )
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("distance")[: (10 - suggested_events.count())]
            )

            suggested_events = close_events.union(suggested_events).order_by(
                "start_time"
            )

        organized_events = (
            Event.objects.upcoming(published_only=False)
            .filter(organizers=person)
            .exclude(visibility=Event.VISIBILITY_ADMIN)
            .order_by("start_time")
        )
        past_organized_events = Paginator(
            Event.objects.past()
            .filter(organizers=person)
            .order_by("-start_time", "-end_time"),
            5,
        ).get_page(self.request.GET.get("past_organized_events_page"))

        past_reports = (
            Event.objects.past()
            .exclude(rsvps__person=person)
            .exclude(report_content="")
            .filter(
                start_time__gt=timezone.now() - timedelta(days=30), do_not_list=False
            )
            .order_by("-start_time")
        )
        if person.coordinates is not None:
            past_reports = past_reports.annotate(
                distance=Distance("coordinates", person.coordinates)
            ).order_by("distance")[:5]

        payments = person.payments.filter(status=Payment.STATUS_COMPLETED).order_by(
            "-created"
        )

        kwargs.update(
            {
                "person": person,
                "rsvped_events": rsvped_events,
                "members_groups": members_groups,
                "promo_code_delay": promo_code_delay,
                "suggested_events": suggested_events,
                "last_events": last_events,
                "past_reports": past_reports,
                "organized_events": organized_events,
                "past_organized_events": past_organized_events,
                "payments": payments,
            }
        )
        return super().get_context_data(**kwargs)


class DashboardSearchView(TemplateView):
    """Vue pour rechercher et lister des groupes et des événéments
    """

    template_name = "people/dashboard_search.html"
    querysets = {
        "upcoming_events": Event.objects.upcoming().filter(
            visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
        ),
        "past_events": Event.objects.past().filter(
            visibility=Event.VISIBILITY_PUBLIC, do_not_list=False
        ),
        "support_groups": SupportGroup.objects.filter(published=True),
    }

    def get_context_data(self, **kwargs):
        q = self.request.GET.get("q")

        if q is None:
            q = ""

        support_groups = self.querysets["support_groups"]
        upcoming_events = self.querysets["upcoming_events"]
        past_events = self.querysets["past_events"]

        if (
            self.request.user.is_authenticated
            and hasattr(self.request.user, "person")
            and self.request.user.person.is_2022_only
        ):
            upcoming_events = upcoming_events.is_2022()
            past_events = past_events.is_2022()
            support_groups = support_groups.is_2022()

        support_groups = support_groups.search(q).order_by("name")[:20]

        upcoming_events = upcoming_events.search(q).order_by(
            "-start_time", "-end_time"
        )[:20]

        past_events = past_events.search(q).order_by("-start_time", "-end_time")[:10]

        result_count = (
            int(support_groups.count())
            + int(upcoming_events.count())
            + int(past_events.count())
        )

        event_count = int(upcoming_events.count()) + int(past_events.count())

        kwargs.update(
            {
                "query": q,
                "result_count": result_count,
                "event_count": event_count,
                "support_groups": support_groups,
                "upcoming_events": upcoming_events,
                "past_events": past_events,
            }
        )

        return super().get_context_data(**kwargs)
