from django.db.models import Count

from people.models import Person
from groups.models import SupportGroup
from events.models import Event, EventSubtype

def get_general_stats(start, end):
    return {
        'new_supporters': Person.objects.filter(created__range=(start, end)).count(),
        'new_groups': SupportGroup.objects.filter(created__range=(start, end)).count(),
        'new_events': Event.objects.filter(created__range=(start, end)).count(),
        'events_happened': Event.objects.filter(start_time__range=(start, end)).count(),
    }

def get_events_by_subtype(start, end):
    subtypes = {s.pk: s.label for s in EventSubtype.objects.all()}
    return {subtypes[c['subtype']]: c['count'] for c in Event.objects.values('subtype').annotate(count=Count('subtype'))}
