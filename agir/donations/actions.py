from urllib.parse import urljoin

import reversion
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from reversion.models import Version

from agir.donations.models import Operation, SpendingRequest, Document, Spending
from agir.lib.display import display_price
from agir.lib.utils import front_url
from agir.people.models import Person


def get_balance(group):
    return (
        Operation.objects.filter(group=group).aggregate(sum=Sum("amount"))["sum"] or 0
    )


def group_can_handle_allocation(group):
    return group.subtypes.filter(label__in=settings.CERTIFIED_GROUP_SUBTYPES).exists()


def get_spending_request_field_label(f):
    return str(SpendingRequest._meta.get_field(f).verbose_name)


def can_be_sent(spending_request):
    return any(
        d.type == Document.TYPE_INVOICE for d in spending_request.documents.all()
    )


def are_funds_sufficient(spending_request):
    return spending_request.amount <= get_balance(spending_request.group)


def admin_summary(spending_request):
    shown_fields = [
        "id",
        "title",
        "status",
        "group",
        "event",
        "category",
        "category_precisions",
        "explanation",
        "amount",
        "spending_date",
        "provider",
        "iban",
    ]

    values = {f: getattr(spending_request, f) for f in shown_fields}

    values["group"] = format_html(
        '<a href="{group_link}">{group_name}</a> ({group_balance})<br><a href="mailto:{group_email}">{group_email}</a><br>{group_phone}',
        group_name=spending_request.group.name,
        group_email=spending_request.group.contact_email,
        group_phone=spending_request.group.contact_phone,
        group_link=front_url("view_group", args=(spending_request.group_id,)),
        group_balance=display_price(get_balance(spending_request.group)),
    )

    values["amount"] = display_price(spending_request.amount)

    return [
        {"label": SpendingRequest._meta.get_field(f).verbose_name, "value": values[f]}
        for f in shown_fields
    ]


def summary(spending_request):
    """Renvoie un résumé de la demande de dépense pour l'affichage sur la page de gestion

    :param spending_request: la demande de dépense à résumer
    :return: un itérateur vers les différents champs constituant le résumé
    """

    other_display_fields = [
        "category_precisions",
        "explanation",
        "spending_date",
        "provider",
        "iban",
    ]

    yield {"label": "Identifiant de la demande", "value": str(spending_request.pk)[:6]}
    yield {
        "label": get_spending_request_field_label("title"),
        "value": spending_request.title,
    }

    status = spending_request.get_status_display()
    if spending_request.status == SpendingRequest.STATUS_DRAFT and can_be_sent(
        spending_request
    ):
        status = _(
            "Dès que votre brouillon est complet, vous pouvez le confirmer pour validation par l'équipe de suivi."
        )

    if spending_request.status in SpendingRequest.STATUS_NEED_ACTION:
        status = format_html("<strong>{}</strong>", status)
    yield {"label": get_spending_request_field_label("status"), "value": status}

    balance = get_balance(spending_request.group)

    amount_text = display_price(spending_request.amount)
    if spending_request.amount > balance:
        amount_text = format_html(
            "{}<br><strong style=\"color: #BB1111;\">L'allocation de votre groupe est pour l'instant insuffisante, votre"
            " demande ne pourra pas être validée</strong>",
            amount_text,
        )

    yield {"label": get_spending_request_field_label("amount"), "value": amount_text}
    yield {
        "label": get_spending_request_field_label("event"),
        "value": format_html(
            '<a href="{link}">{name}</a>',
            link=reverse("view_event", kwargs={"pk": spending_request.event.id}),
            name=spending_request.event.name,
        )
        if spending_request.event
        else _("Aucun"),
    }
    yield {
        "label": get_spending_request_field_label("category"),
        "value": spending_request.get_category_display(),
    }

    for f in other_display_fields:
        yield {
            "label": get_spending_request_field_label(f),
            "value": getattr(spending_request, f),
        }


DIFFED_FIELDS = [
    "title",
    "event",
    "category",
    "category_precisions",
    "explanation",
    "amount",
    "spending_date",
    "provider",
    "iban",
]


def get_diff(before, after):
    return [
        get_spending_request_field_label(f)
        for f in DIFFED_FIELDS
        if after.get(f) != before.get(f)
    ]


HISTORY_MESSAGES = {
    SpendingRequest.STATUS_DRAFT: "Création de la demande",
    SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION: "Validé par l'auteur d'origine",
    SpendingRequest.STATUS_AWAITING_REVIEW: "Renvoyé pour validation à l'équipe de suivi des questions financières",
    SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION: "Informations supplémentaires requises",
    SpendingRequest.STATUS_VALIDATED: "Demande validée par l'équipe de suivi des questions financières",
    SpendingRequest.STATUS_TO_PAY: "Demande en attente de réglement",
    SpendingRequest.STATUS_PAID: "Demande réglée",
    SpendingRequest.STATUS_REFUSED: "Demande rejetée par l'équipe de suivi des questions financières",
    (
        SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION,
        SpendingRequest.STATUS_AWAITING_REVIEW,
    ): "Validé par un⋅e second⋅e animateur⋅rice",
}
for status, label in SpendingRequest.STATUS_CHOICES:
    HISTORY_MESSAGES[(status, status)] = "Modification de la demande"


def get_history_step(old, new, admin):
    old_fields = old.field_dict if old else {}
    new_fields = new.field_dict
    old_status, new_status = old_fields.get("status"), new_fields["status"]
    revision = new.revision
    person = revision.user.person if revision.user else None

    res = {
        "modified": new_fields["modified"],
        "comment": revision.get_comment(),
        "diff": get_diff(old_fields, new_fields) if old_fields else [],
    }

    if person and admin:
        res["user"] = format_html(
            '<a href="{url}">{text}</a>',
            url=reverse("admin:people_person_change", args=[person.pk]),
            text=person.get_short_name(),
        )
    elif person:
        res["user"] = person.get_short_name()
    else:
        res["user"] = "Équipe de suivi"

    # cas spécifique : si on revient à "attente d'informations supplémentaires suite à une modification par un non admin
    # c'est forcément une modification
    if (
        new_status == SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION
        and person is not None
    ):
        res["title"] = "Modification de la demande"
    # some couples (old_status, new_status)
    elif (old_status, new_status) in HISTORY_MESSAGES:
        res["title"] = HISTORY_MESSAGES[(old_status, new_status)]
    else:
        res["title"] = HISTORY_MESSAGES.get(new_status, "[Modification non identifiée]")

    return res


def history(spending_request, admin=False):
    versions = (
        Version.objects.get_for_object(spending_request)
        .order_by("pk")
        .select_related("revision__user__person")
    )

    previous_version = None

    for version in versions:
        yield get_history_step(previous_version, version, admin)
        previous_version = version


def _get_first_validator(spending_request):
    versions = (
        Version.objects.get_for_object(spending_request)
        .order_by("pk")
        .select_related("revision__user")
    )
    try:
        return next(
            v.revision.user
            for v in versions
            if v.field_dict["status"]
            == SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION
        )
    except StopIteration:
        return None


EDITABLE_STATUSES = [
    SpendingRequest.STATUS_DRAFT,
    SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION,
    SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
    SpendingRequest.STATUS_AWAITING_REVIEW,
    SpendingRequest.STATUS_VALIDATED,
]


def can_edit(spending_request):
    return spending_request.status in EDITABLE_STATUSES


def can_send_for_review(spending_request, user):
    """Check if user can send spending_request for review

    :param spending_request: the spending_request to check
    :param user: the user that could send for review
    :return: boolean
    """

    # the spending request must has at least one invoice
    if not can_be_sent(spending_request):
        return False

    # the user can always send for review in any of these two states
    if spending_request.status in [
        SpendingRequest.STATUS_DRAFT,
        SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
    ]:
        return True

    # in AWAITING_GROUP_VALIDATION, we need a second manager to confirm
    # we check that user has not already confirmed the request
    return user != _get_first_validator(spending_request)


TRANSFER_STATES_MAP = {
    SpendingRequest.STATUS_DRAFT: SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION,
    SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION: SpendingRequest.STATUS_AWAITING_REVIEW,
    SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION: SpendingRequest.STATUS_AWAITING_REVIEW,
}


def get_current_action(spending_request, user):
    if spending_request.status in TRANSFER_STATES_MAP:
        if not can_be_sent(spending_request):
            return {
                "button": None,
                "explanation": "Avant de pouvoir être envoyée pour validation, votre demande de dépense doit être"
                " complète et comporter au moins une facture.",
            }

        if spending_request.status == SpendingRequest.STATUS_DRAFT:
            return {
                "button": "Valider",
                "explanation": "Une fois votre brouillon terminé, vous pouvez le valider ci-dessous. Avant qu'il ne soit"
                " transmis à l'équipe de suivi des questions financières, il devra d'abord être validé par un autre des"
                " animateurs ou gestionnaires de votre groupe d'action.",
            }
        elif (
            spending_request.status == SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION
        ):
            if not can_send_for_review(spending_request, user):
                return {
                    "button": None,
                    "explanation": "Vous avez déjà validé cette demande. Avant sa transmission à l'équipe de suivi des"
                    " questions financières, elle doit tout d'abord être validé par un⋅e autre"
                    " animateur⋅rice ou gestionnaire",
                }
            else:
                return {
                    "button": "Transmettre",
                    "explanation": "Cette demande a déjà été validé par un⋅e animateur⋅rice ou gestionnaire du groupe."
                    "Pour permettre sa transmission, elle doit encore être validée par un deuxième animateur⋅rice ou"
                    " gestionnaire.",
                }
        else:
            return {
                "button": "Transmettre",
                "explanation": "Lorsque vous aurez intégré les modifications demandées, vous pourrez de nouveau"
                " transmettre cette demande à l'équipe de suivi.",
            }

    if spending_request.status == SpendingRequest.STATUS_AWAITING_REVIEW:
        return {
            "button": None,
            "explanation": "Votre demande est en cours d'évaluation par l'équipe de suivi des questions financières."
            "Vous serez prévenus une fois celle-ci traitée.",
        }

    if spending_request.status == SpendingRequest.STATUS_VALIDATED:
        if are_funds_sufficient(spending_request):
            return {
                "button": "Demander le paiement",
                "explanation": "L'allocation de votre groupe est maintenant suffisante pour permettre le paiement de"
                " cette demande.",
            }
        else:
            return {
                "button": None,
                "explanation": "Votre groupe ne dispose pas d'une allocation suffisante pour obtenir le réglement de"
                " cette demande pour le moment. Dès que votre allocation sera suffisante, vous pourrez demander le"
                " paiement de cette demande avec ce formulaire.",
            }

    if spending_request.status == SpendingRequest.STATUS_TO_PAY:
        return {
            "button": None,
            "explanation": "Votre demande est en attente de paiement par l'équipe de suivi. Cela ne devrait pas tarder !",
        }

    if spending_request.status == SpendingRequest.STATUS_PAID:
        return {
            "button": None,
            "explanation": "Votre demande a été correctement réglée.",
        }

    return {
        "button": None,
        "explanation": "Votre demande a été refusée car elle ne rentrait pas dans le cadre des demandes de dépense/",
    }


def validate_action(spending_request, user):
    """Valide la requête pour vérification pour l'administration, ou confirme la demande de paiement

    :param spending_request:
    :param user:
    :return: whether the spending request was successfully sent for review
    """

    if spending_request.status == SpendingRequest.STATUS_VALIDATED:
        try:
            with reversion.create_revision(atomic=True):
                reversion.set_user(user)
                spending_request.operation = Spending.objects.create(
                    group=spending_request.group, amount=-spending_request.amount
                )
                spending_request.status = SpendingRequest.STATUS_TO_PAY
                spending_request.save()
        except IntegrityError:
            return False
        return True

    if spending_request.status not in TRANSFER_STATES_MAP or not can_send_for_review(
        spending_request, user
    ):
        return False

    with reversion.create_revision():
        reversion.set_user(user)
        spending_request.status = TRANSFER_STATES_MAP[spending_request.status]
        spending_request.save()

    return True


def find_or_create_person_from_payment(payment):
    if payment.person is None:
        try:
            payment.person = Person.objects.get_by_natural_key(payment.email)
            if payment.meta.get("subscribed"):
                payment.person.subscribed = True
                payment.person.save()
        except Person.DoesNotExist:
            person_fields = [f.name for f in Person._meta.get_fields()]
            payment.person = Person.objects.create_person(
                email=payment.email,
                **{k: v for k, v in payment.meta.items() if k in person_fields}
            )
        payment.save()
