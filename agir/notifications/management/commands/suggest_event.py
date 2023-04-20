from django.contrib.humanize.templatetags.humanize import apnumber
from django.utils import timezone
from django.utils.translation import ngettext

from agir.activity.models import Activity
from agir.events.actions.notifications import new_event_suggestion_notification
from agir.events.models import Event
from agir.lib.commands import BaseCommand
from agir.lib.management_utils import segment_argument
from agir.people.models import Person


class Command(BaseCommand):
    help = "suggest an event to each user"
    queryset = (
        Event.objects.listed()
        .exclude(coordinates=None)
        .exclude(subtype__for_organizer_group_members_only=True)
    )

    def add_arguments(self, parser):
        parser.add_argument("-S", "--segment", type=segment_argument)

    def get_recipients(self, segment=None):
        if segment:
            queryset = segment.get_subscribers_queryset()
        else:
            queryset = Person.objects.with_active_role()

        return (
            queryset.exclude(coordinates=None)
            .filter(
                role__last_login__gt=timezone.now() - timezone.timedelta(days=60),
            )  # seulement les gens s'étant déjà connectés dans les 2 derniers mois
            .exclude(
                activities__in=Activity.objects.filter(
                    type=Activity.TYPE_EVENT_SUGGESTION,
                    created__gt=timezone.now() - timezone.timedelta(hours=18),
                )
            )  # exclure les personnes ayant déjà reçu une suggestion aujourd'hui
        )

    def get_event_for_person(self, person):
        return (
            self.queryset.filter(
                start_time__lt=timezone.now() + timezone.timedelta(days=7)
            )
            .exclude(attendees=person)
            .near(coordinates=person.coordinates, radius=person.action_radius)
            .order_by("distance")
            .first()
        )

    def notify(self, person, event=None):
        if event is None:
            self.warning(f"No event found for person #{person.id}")
            return

        if not self.dry_run:
            new_event_suggestion_notification(event, person)
            # Avoid sending event suggestions via email until stricter rules are defined
            # send_event_suggestion_email.delay(near_event.pk, person.pk)

        self.success(
            f"One event found {round(event.distance.m) / 1000} Km for person #{person.id}"
        )

    def handle(self, segment, *args, **options):
        recipients = list(self.get_recipients(segment))
        recipient_count = len(recipients)

        if recipient_count == 0:
            self.error("No recipients for event suggestion have been found")
            return

        self.init_tqdm(total=recipient_count)
        self.info(
            ngettext(
                f"⌛ Looking for event suggestions for one person...",
                f"⌛ Looking for event suggestions for {apnumber(recipient_count)} people...",
                recipient_count,
            )
        )

        notification_count = 0
        for person in recipients:
            self.log_current_item(person.pk)
            event = self.get_event_for_person(person)
            self.notify(person, event)
            self.tqdm.update(1)
            if event:
                notification_count += 1

        self.log_current_item("")
        self.tqdm.close()
        self.success(
            ngettext(
                f"One event suggestion has been notified",
                f"{apnumber(notification_count)} event suggestions have been notified",
                notification_count,
            )
        )
