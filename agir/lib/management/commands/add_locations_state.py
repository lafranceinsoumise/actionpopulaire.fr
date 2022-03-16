from agir.groups.models import SupportGroup
from agir.events.models import Event
from django.db.models import Q
from django.core.management import BaseCommand


class Command(BaseCommand):
    def print_line(self, line):
        self.stdout.write(f"   {line}")

    def update_groups_state(self):
        groups = SupportGroup.objects.exclude(Q(location_country=""))

        for group in groups:
            country = group.location_country
            group.location_state = country.name

        SupportGroup.objects.bulk_update(groups, ["location_state"])
        self.print_line(f"Updated : {len(groups)} groupes")

    def update_events_state(self):
        events = Event.objects.exclude(Q(location_country=""))

        for event in events:
            country = event.location_country
            event.location_state = country.name

        Event.objects.bulk_update(events, ["location_state"])
        self.print_line(f"Updated : {len(events)} événements")

    def handle(self, *args, **options):

        self.stdout.write("\n")
        self.stdout.write(
            f"** Localisation — remplissage des champs 'state' des groupes et événements **",
            self.style.WARNING,
        )

        self.update_groups_state()
        self.update_events_state()
        self.stdout.write(self.style.SUCCESS("SUCCESS !"))
