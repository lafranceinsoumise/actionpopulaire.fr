import datetime
from django.core.management import BaseCommand
from django.utils import timezone

from events.models import Event
from groups.models import SupportGroup
from people.models import Person


class Command(BaseCommand):
    help='Display weekly statistics'

    def handle(self, *args, **options):
        print('Plateforme')
        today = timezone.now()
        last_monday = today - datetime.timedelta(days=today.weekday())
        last_monday = last_monday.replace(hour=0, minute=0, second=0)
        one_week_ago = last_monday - datetime.timedelta(days=7)
        two_weeks_ago = one_week_ago - datetime.timedelta(days=7)
        three_weeks_ago = two_weeks_ago - datetime.timedelta(days=7)

        new_supports = Person.objects.filter(created__lt=last_monday, created__gt=one_week_ago).count()
        previous_week_new_supports = Person.objects.filter(created__lt=one_week_ago, created__gt=two_weeks_ago).count()
        even_before_new_supports = Person.objects.filter(created__lt=two_weeks_ago, created__gt=three_weeks_ago).count()

        print('{} nouveaux signataires ({} la semaine dernière, {} celle d\'avant)'.format(
            new_supports, previous_week_new_supports, even_before_new_supports
        ))

        new_groups = SupportGroup.objects.filter(created__lt=last_monday, created__gt=one_week_ago, published=True).count()
        previous_week_new_groups = SupportGroup.objects.filter(created__lt=one_week_ago, created__gt=two_weeks_ago, published=True).count()

        print('{} nouveaux groupes ({:+d})'.format(new_groups, new_groups - previous_week_new_groups))

        events = Event.objects.filter(published=True, end_time__lt=last_monday, start_time__gt=one_week_ago).count()
        last_week_events = Event.objects.filter(published=True, end_time__lt=one_week_ago, start_time__gt=two_weeks_ago).count()

        print('{} événements survenus ({:+d})'.format(events, last_week_events))

        meetings = Event.objects.filter(subtype__id=10, published=True, end_time__lt=last_monday, start_time__gt=one_week_ago).count()
        last_week_meetings = Event.objects.filter(subtype__id=10, published=True, end_time__lt=one_week_ago,
                                                start_time__gt=two_weeks_ago).count()

        print('dont {} réunions publiques ({:+d})'.format(meetings, last_week_meetings))