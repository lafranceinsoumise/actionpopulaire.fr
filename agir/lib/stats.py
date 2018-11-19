from django.conf import settings
from django.db.models import Count

from agir.people.models import Person
from agir.groups.models import SupportGroup, Membership
from agir.events.models import Event, EventSubtype


def get_general_stats(start, end):
    return {
        'new_supporters': Person.objects.filter(created__range=(start, end)).count(),
        'new_groups': SupportGroup.objects.filter(published=True, created__range=(start, end)).count(),
        'new_events': Event.objects.filter(published=True, created__range=(start, end)).count(),
        'events_happened': Event.objects.filter(published=True, start_time__range=(start, end)).count(),
        'new_memberships': Person.objects.filter(
            memberships__created__range=(start, end),
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True
        ).exclude(memberships__in=Membership.objects.filter(
            created__lt=start,
            supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP
        )).count()
    }


def get_events_by_subtype(start, end):
    subtypes = {s.pk: s.label for s in EventSubtype.objects.all()}
    return {subtypes[c['subtype']]: c['count'] for c in Event.objects.values('subtype').annotate(count=Count('subtype'))}


def get_instant_stats():
    return {
        'subscribers': Person.objects.filter(subscribed=True, emails___bounced=False).count(),
        'groups': SupportGroup.objects.filter(type=SupportGroup.TYPE_LOCAL_GROUP, published=True).count(),
        'group_members': Person.objects.filter(supportgroups__type=SupportGroup.TYPE_LOCAL_GROUP,
                                               supportgroups__published=True).count(),
        'certified_groups': SupportGroup.objects.filter(subtypes__label=settings.CERTIFIED_GROUP_SUBTYPE,
                                                        published=True).count(),
        'certified_group_members': Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_LOCAL_GROUP,
            supportgroups__subtypes__label=settings.CERTIFIED_GROUP_SUBTYPE,
            supportgroups__published=True
        ).count(),
        'thematic_groups': SupportGroup.objects.filter(type=SupportGroup.TYPE_THEMATIC_BOOKLET, published=True).count(),
        'func_groups': SupportGroup.objects.filter(type=SupportGroup.TYPE_FUNCTIONAL, published=True).count(),
        'pro_groups': SupportGroup.objects.filter(type=SupportGroup.TYPE_PROFESSIONAL, published=True).count(),
    }
