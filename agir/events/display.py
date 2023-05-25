from operator import itemgetter

from django.utils.formats import localize
from django.utils.timezone import get_current_timezone
from glom import T, glom, Val

from agir.payments.models import Payment
from agir.people.person_forms.display import PersonFormDisplay
from agir.people.person_forms.models import PersonFormSubmission
from .models import (
    IdentifiedGuest,
)

SPEC_RSVP = {
    "id": ("id", "R{}".format),
    "created": (T.created.astimezone(get_current_timezone()), localize),
    "person_id": ("person_id", str),
    "email": "person.email",
    "status": T.get_status_display(),
}

IG_ID = lambda ig: f"R{ig.rsvp_id}I{ig.id}"

SPEC_IDENTIFIED_GUEST = {
    "id": IG_ID,
    "created": (T.submission.created.astimezone(get_current_timezone()), localize),
    "person_id": ("rsvp.person_id", str),
    "email": "rsvp.person.email",
    "status": T.get_status_display(),
}

SPEC_PAYMENT = {
    "montant": ("price", T / 100),
    "status_paiement": T.get_status_display(),
    "mode de paiement": "mode",
}


def display_participants(event):
    headers = list(SPEC_RSVP)

    rsvps = event.rsvps.select_related("person")
    values = glom(rsvps, [(SPEC_RSVP, T.values(), list)])

    guests = IdentifiedGuest.objects.filter(rsvp__event=event)
    values += glom(guests, [(SPEC_IDENTIFIED_GUEST, T.values(), list)])

    payments_id = [r.payment_id for r in rsvps] + [g.payment_id for g in guests]
    existing_payments_id = [i for i in payments_id if i is not None]
    submissions_id = [r.form_submission_id for r in rsvps] + [
        g.submission_id for g in guests
    ]
    existing_submissions_id = [i for i in submissions_id if i is not None]

    if existing_payments_id:
        payments = Payment.objects.filter(id__in=existing_payments_id)
        payment_values = {
            p.id: glom(p, (SPEC_PAYMENT, T.values(), list)) for p in payments
        }

        headers += list(SPEC_PAYMENT)
        empty = [""] * len(headers)

        for val, i in zip(values, payments_id):
            val.extend(payment_values.get(i, empty))

    if existing_submissions_id:
        display = PersonFormDisplay()
        submissions = PersonFormSubmission.objects.filter(
            id__in=existing_submissions_id
        )
        sub_headers, sub_values = display.get_formatted_submissions(
            submissions, html=False, include_admin_fields=False
        )
        sub_headers = [str(s) for s in sub_headers]
        headers.extend(sub_headers)

        sub_values = {sub.id: v for sub, v in zip(submissions, sub_values)}
        empty = [""] * (len(sub_headers) - 2)

        for val, i in zip(values, submissions_id):
            val.extend(sub_values.get(i, empty))

    headers = [str(s) for s in headers]

    values = sorted(values, key=itemgetter(0))

    return [headers, *values]


def display_rsvp(rsvp):
    values = glom(rsvp, (SPEC_RSVP))

    if rsvp.payment:
        values.update(glom(rsvp.payment, SPEC_PAYMENT))

    if rsvp.form_submission:
        display = PersonFormDisplay()
        res = display.get_formatted_submission(
            rsvp.form_submission, include_admin_fields=False, html=False
        )
        values.update({str(d["label"]): d["value"] for fs in res for d in fs["data"]})

    return values


def display_identified_guest(ig):
    values = glom(ig, (SPEC_IDENTIFIED_GUEST))

    if ig.payment:
        values.update(glom(ig.payment, SPEC_PAYMENT))

    if ig.submission:
        display = PersonFormDisplay()
        res = display.get_formatted_submission(
            ig.submission, include_admin_fields=False, html=False
        )
        values.update({str(d["label"]): d["value"] for fs in res for d in fs["data"]})

    return values
