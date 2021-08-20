import csv
import sys

from django.core.management import BaseCommand

from agir.events.models import RSVP
from agir.lib.display import display_price
from agir.lib.management_utils import event_argument


class Command(BaseCommand):
    help = "Extract people for event to import in scanner (convenient if there is no placement)"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument("event", type=event_argument)
        parser.add_argument("category_field", type=str)

    def handle(self, event, category_field, **kwargs):
        writer = csv.writer(sys.stdout)
        writer.writerow(
            [
                "numero",
                "canceled",
                "full_name",
                "uuid",
                "contact_email",
                "gender",
                "category",
                "price",
                "status",
            ]
        )

        for i, rsvp in enumerate(
            event.rsvps.filter(form_submission__isnull=False)
            .select_related("person", "form_submission")
            .order_by("created")
        ):
            writer.writerow(
                [
                    "R" + str(rsvp.pk),
                    "O" if rsvp.status == RSVP.STATUS_CANCELED else "",
                    f"{rsvp.form_submission.data.get('first_name')} {rsvp.form_submission.data.get('last_name')}",
                    str(rsvp.person.id),
                    rsvp.person.email,
                    rsvp.person.gender or "",
                    rsvp.form_submission.data.get(category_field, ""),
                    display_price(event.get_price(rsvp.form_submission.data)),
                    "completed" if rsvp.status == RSVP.STATUS_CONFIRMED else "on-hold",
                ]
            )
            for j, guest in enumerate(
                rsvp.identified_guests.select_related("submission").order_by("id")
            ):
                writer.writerow(
                    [
                        "G" + str(rsvp.pk) + "g" + str(guest.pk),
                        "O" if guest.status == RSVP.STATUS_CANCELED else "",
                        f"{guest.submission.data['first_name']} {guest.submission.data['last_name']}",
                        str(rsvp.person.id),
                        rsvp.person.email,
                        guest.submission.data.get("gender", ""),
                        guest.submission.data.get(category_field, ""),
                        display_price(event.get_price(guest.submission.data)),
                        "completed"
                        if guest.status == RSVP.STATUS_CONFIRMED
                        else "on-hold",
                    ]
                )
