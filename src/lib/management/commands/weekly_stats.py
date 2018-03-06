import datetime
import pytz
from django.core.management import BaseCommand, CommandError
from django.utils import timezone

from events.models import Event
from groups.models import SupportGroup
from people.models import Person


class Command(BaseCommand):
    help = 'Display weekly statistics'

    date_format = '%Y/%m/%d'

    def add_arguments(self, parser):
        parser.add_argument('start', nargs='?', default=None, metavar='START', help='the start date')
        parser.add_argument('--timezone', default=None, metavar='TIMEZONE', help='name of the timezone', dest='tz')

    def handle(self, *args, start, tz, **options):
        tz = pytz.timezone(tz) if tz else timezone.get_current_timezone()

        period = week = timezone.timedelta(days=7)
        period_name = 'semaine'

        today = timezone.now().astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        last_monday = today - datetime.timedelta(days=today.weekday())

        if start is None:
            end = last_monday
            start = last_monday - period
        else:
            try:
                start = timezone.datetime.strptime(start, self.date_format).replace(
                    tzinfo=timezone.get_default_timezone())
            except ValueError:
                raise CommandError('START is not a valid date (YYYY/mm/dd)')

            end = start + week

            if end > today:
                end = today
                period = end - start
                period_name = 'période'

        one_period_before = start - period
        two_period_before = start - 2 * period

        self.stdout.write(
            f'Plateforme - du {start.strftime(self.date_format)} au {(end-timezone.timedelta(days=1)).strftime(self.date_format)}')
        if period != week:
            self.stdout.write("Attention : durée de moins d'une semaine, périodes non comparables")
        self.stdout.write('\n')

        new_supports = Person.objects.filter(created__range=(start, end)).count()
        previous_period_new_supports = Person.objects.filter(created__range=(one_period_before, start)).count()
        even_before_new_supports = Person.objects.filter(created__range=(two_period_before, one_period_before)).count()

        print('{} nouveaux signataires ({} la {period} précédente, {} celle d\'avant)'.format(
            new_supports, previous_period_new_supports, even_before_new_supports, period=period_name
        ))

        new_groups = SupportGroup.objects.filter(created__range=(start, end), published=True).count()
        previous_week_new_groups = SupportGroup.objects.filter(created__range=(one_period_before, start),
                                                               published=True).count()

        print('{} nouveaux groupes ({:+d})'.format(new_groups, new_groups - previous_week_new_groups))

        events = Event.objects.filter(published=True, end_time__range=(start, end)).count()
        last_week_events = Event.objects.filter(published=True, end_time__range=(one_period_before, start)).count()

        print('{} événements survenus ({:+d})'.format(events, last_week_events))

        meetings = Event.objects.filter(subtype__id=10, published=True, end_time__range=(start, end)).count()
        last_week_meetings = Event.objects.filter(subtype__id=10, published=True, end_time__range=(one_period_before, start)).count()

        print('dont {} réunions publiques ({:+d})'.format(meetings, last_week_meetings))
