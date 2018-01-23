from datetime import timedelta

from django.contrib.gis.db.models.functions import Distance
from django.utils import timezone
from django.db.models import Q, F, Value, TextField
from django.views.generic import TemplateView

from events.models import Event
from front.view_mixins import SoftLoginRequiredMixin
from groups.models import SupportGroup

from lib.tasks import geocode_person


class DashboardView(SoftLoginRequiredMixin, TemplateView):
    template_name = 'front/dashboard.html'

    def get(self, request, *args, **kwargs):
        person = request.user.person

        if person.coordinates_type is None:
            geocode_person.delay(person.pk)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        rsvped_events = Event.objects.upcoming().annotate(distance=Distance('coordinates', person.coordinates))\
            .filter(attendees=person).order_by('start_time', 'end_time')
        members_groups = SupportGroup.objects.filter(memberships__person=person, published=True).order_by('name')\
            .annotate(user_is_manager=F('memberships__is_manager')._combine(F('memberships__is_referent'), 'OR', False))

        suggested_events = Event.objects.upcoming()\
            .exclude(rsvps__person=person)\
            .filter(Q(organizers_groups__in=person.supportgroups.all()) & ~Q(attendees=person)) \
            .annotate(reason=Value('Cet événément est organisé par un groupe dont vous êtes membre.', TextField()))\
            .annotate(distance=Distance('coordinates', person.coordinates))
        if person.coordinates is not None:
            suggested_events = suggested_events

        last_events = Event.objects.past().filter(Q(attendees=person) | Q()).order_by('-start_time', '-end_time')[:10]

        if person.coordinates is not None and len(suggested_events) < 10:
            close_events = Event.objects.upcoming().filter(start_time__lt=timezone.now() + timedelta(days=30)) \
                .exclude(rsvps__person=person)\
                .annotate(reason=Value('Cet événement se déroule près de chez vous.', TextField()))\
                .annotate(distance=Distance('coordinates', person.coordinates))\
                .order_by('distance')[:(10 - suggested_events.count())]

            suggested_events = close_events.union(suggested_events).order_by('start_time')


        organized_events = Event.objects.upcoming().filter(organizers=person).order_by('start_time')
        past_organized_events = Event.objects.past().filter(organizers=person).order_by('-start_time', '-end_time')[:10]

        kwargs.update({
            'person': person,
            'rsvped_events': rsvped_events, 'members_groups': members_groups,
            'suggested_events': suggested_events, 'last_events': last_events,
            'organized_events': organized_events, 'past_organized_events': past_organized_events
        })

        return super().get_context_data(**kwargs)
