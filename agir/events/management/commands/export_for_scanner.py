import csv
import sys

from agir.people.models import PersonEmail
from django.core.management import BaseCommand

from agir.events.models import RSVP, IdentifiedGuest
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
                "_contact_emails",
                "gender",
                "category",
                "price",
                "status",
                "entry",
            ]
        )

        rsvps = event.rsvps.filter(form_submission__isnull=False).select_related(
            "person",
            "form_submission",
            "payment",
        )
        guests = IdentifiedGuest.objects.filter(
            rsvp__event_id=event.id,
        ).select_related("rsvp__person", "submission", "payment")

        # Pour éviter
        emails = PersonEmail.objects.raw(
            """
            WITH emails AS (
              SELECT
              pe.id,
              pe.person_id,
              pe.address,
              row_number() OVER (PARTITION BY pe.person_id ORDER BY pe.person_id, _order) AS num
              FROM people_personemail pe
              JOIN people_person p ON p.id = pe.person_id
              JOIN events_rsvp r on p.id = r.person_id
              WHERE r.event_id = %s AND NOT pe.bounced
            )
            SELECT id, person_id, address FROM emails WHERE num = 1;
            """,
            [event.id],
        )
        emails = {e.person_id: e.address for e in emails}

        for rsvp in rsvps:
            writer.writerow(
                [
                    "R" + str(rsvp.pk),
                    "O" if rsvp.status == RSVP.STATUS_CANCELED else "",
                    f"{rsvp.form_submission.data.get('first_name')} {rsvp.form_submission.data.get('last_name')}",
                    str(rsvp.person_id),
                    emails.get(rsvp.person_id, None) or rsvp.person.email,
                    rsvp.person.gender or "",
                    rsvp.form_submission.data.get(category_field, ""),
                    display_price(rsvp.payment.price if rsvp.payment else 0),
                    "completed" if rsvp.status == RSVP.STATUS_CONFIRMED else "on-hold",
                    rsvp.created.isoformat()
                    if rsvp.form_submission.data.get("admin", False)
                    else None,
                ]
            )
        for guest in guests:
            writer.writerow(
                [
                    "G" + str(guest.rsvp_id) + "g" + str(guest.pk),
                    "O" if guest.status == RSVP.STATUS_CANCELED else "",
                    f"{guest.submission.data['first_name']} {guest.submission.data['last_name']}",
                    str(guest.rsvp.person_id),
                    emails.get(guest.rsvp.person_id, None) or guest.rsvp.person.email,
                    guest.submission.data.get("gender", ""),
                    guest.submission.data.get(category_field, ""),
                    display_price(guest.payment.price if guest.payment else 0),
                    "completed" if guest.status == RSVP.STATUS_CONFIRMED else "on-hold",
                    None,
                ]
            )
