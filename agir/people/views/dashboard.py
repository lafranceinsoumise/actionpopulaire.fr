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


class SearchView(TemplateView):
    """Vue pour rechercher et lister des groupes et des événéments"""

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
