from django.db.models import Q, F
from django.views.generic import TemplateView

from django.utils import timezone
from events.models import Event
from front.view_mixins import SoftLoginRequiredMixin
from groups.models import SupportGroup


class DashboardView(SoftLoginRequiredMixin, TemplateView):
    template_name = 'front/dashboard.html'

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        rsvped_events = Event.objects.upcoming().filter(attendees=person).order_by('start_time', 'end_time')
        members_groups = SupportGroup.objects.filter(memberships__person=person, published=True).order_by('name')\
            .annotate(user_is_manager=F('memberships__is_manager')._combine(F('memberships__is_referent'), 'OR', False))

        suggested_events = [
            (event, 'Cet événément est organisé par un groupe dont vous êtes membre.')
            for event in Event.objects.upcoming()
                .filter(Q(organizers_groups__in=person.supportgroups.all()) & ~Q(attendees=person))
                .order_by('start_time', 'end_time')
        ]
        last_events = Event.objects.past().filter(attendees=person).order_by('-start_time', '-end_time')[:10]

        organized_events = Event.objects.upcoming().filter(organizers=person)

        kwargs.update({
            'person': person,
            'rsvped_events': rsvped_events, 'members_groups': members_groups,
            'suggested_events': suggested_events, 'last_events': last_events,
            'organized_events': organized_events
        })

        return super().get_context_data(**kwargs)
