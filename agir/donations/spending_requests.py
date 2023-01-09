import reversion
from django.db import IntegrityError
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from glom import glom, T
from reversion.models import Version

from agir.donations.allocations import get_supportgroup_balance
from agir.donations.models import SpendingRequest, Spending, Document
from agir.donations.tasks import send_spending_request_to_review_email
from agir.lib.display import display_price
from agir.lib.utils import front_url


def group_formatter(group):
    return format_html(
        '<a href="{group_link}">{group_name}</a> ({group_balance})<br><a href="mailto:{group_email}">{group_email}</a><br>{group_phone}',
        group_name=group.name,
        group_email=group.contact_email,
        group_phone=group.contact_phone,
        group_link=front_url("view_group", args=(group.id,)),
        group_balance=display_price(get_supportgroup_balance(group)),
    )


def admin_summary(spending_request):
    spec = {
        "id": "id",
        "title": "title",
        "status": T.get_status_display(),
        "group": ("group", group_formatter),
        "event": "event",
        "category": T.get_category_display(),
        "category_precisions": "category_precisions",
        "explanation": "explanation",
        "amount": ("amount", display_price),
        "spending_date": "spending_date",
        "provider": "provider",
        "iban": "iban",
        "payer_name": "payer_name",
    }

    values = glom(spending_request, spec)

    return [
        {"label": get_spending_request_field_label(f), "value": values[f]} for f in spec
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
        "payer_name",
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

    balance = get_supportgroup_balance(spending_request.group)

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


DELETABLE_STATUSES = [
    SpendingRequest.STATUS_DRAFT,
    SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION,
]


def can_delete(spending_request):
    return spending_request.status in DELETABLE_STATUSES


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
                "explanation": "Avant de pouvoir être envoyée pour validation, votre demande doit être"
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
        if spending_request.status == SpendingRequest.STATUS_AWAITING_REVIEW:
            send_spending_request_to_review_email.delay(spending_request.pk)
        spending_request.save()

    return True


def get_spending_request_field_label(f):
    return str(SpendingRequest._meta.get_field(f).verbose_name)


def can_be_sent(spending_request):
    return any(
        d.type == Document.TYPE_INVOICE for d in spending_request.documents.all()
    )


def are_funds_sufficient(spending_request):
    return spending_request.amount <= get_supportgroup_balance(spending_request.group)
