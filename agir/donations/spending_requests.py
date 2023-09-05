import reversion
from django.db import IntegrityError
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _, ngettext
from glom import glom, T

from agir.donations.allocations import get_supportgroup_balance
from agir.donations.models import SpendingRequest, Spending
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
        "campaign": "campaign",
        "category": T.get_category_display(),
        "category_precisions": "category_precisions",
        "explanation": "explanation",
        "amount": ("amount", display_price),
        "spending_date": "spending_date",
        "bank_account_name": "bank_account_name",
        "bank_account_iban": "bank_account_iban",
        "bank_account_bic": "bank_account_bic",
        "contact_name": "contact_name",
        "contact_phone": "contact_phone",
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
        "explanation",
        "spending_date",
        "contact_name",
        "contact_phone",
        "bank_account_name",
        "bank_account_iban",
        "bank_account_bic",
        "bank_account_rib",
    ]

    yield {"label": "Identifiant de la demande", "value": str(spending_request.pk)[:6]}
    yield {
        "label": get_spending_request_field_label("title"),
        "value": spending_request.title,
    }

    status = spending_request.get_status_display()
    if spending_request.ready_for_review:
        status = _(
            "Dès que votre brouillon est complet, vous pouvez le confirmer pour validation par l'équipe de suivi."
        )

    if spending_request.need_action:
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


STATUS_EXPLANATION = {
    SpendingRequest.Status.AWAITING_PEER_REVIEW: "Vous avez déjà validé cette demande. Avant sa transmission à l'équipe de suivi des"
    " questions financières, elle doit tout d'abord être validé par un⋅e autre"
    " animateur⋅rice ou gestionnaire",
    SpendingRequest.Status.AWAITING_ADMIN_REVIEW: "Votre demande est en cours d'évaluation par l'équipe de suivi des questions financières."
    "Vous serez prévenus une fois celle-ci traitée.",
    SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION: "Lorsque vous aurez intégré les modifications demandées, vous pourrez de nouveau"
    " transmettre cette demande à l'équipe de suivi.",
    SpendingRequest.Status.VALIDATED: "Votre groupe ne dispose pas d'une allocation suffisante pour obtenir le réglement de"
    " cette demande pour le moment. Dès que votre allocation sera suffisante, vous pourrez demander le"
    " paiement de cette demande avec ce formulaire.",
    SpendingRequest.Status.TO_PAY: "Votre demande est en attente de paiement par l'équipe de suivi. Cela ne devrait pas tarder !",
    SpendingRequest.Status.PAID: "Votre demande a été correctement réglée.",
    SpendingRequest.Status.REFUSED: "Votre demande a été refusée car elle ne rentrait pas dans le cadre des demandes de dépense",
}

NEXT_STATUS_EXPLANATION = {
    SpendingRequest.Status.AWAITING_PEER_REVIEW: "Une fois votre brouillon terminé, vous pouvez le valider ci-dessous. Avant qu'il ne soit"
    " transmis à l'équipe de suivi des questions financières, il devra d'abord être validé par un autre des"
    " animateurs ou gestionnaires de votre groupe d'action.",
    SpendingRequest.Status.AWAITING_ADMIN_REVIEW: {
        SpendingRequest.Status.AWAITING_PEER_REVIEW: "Cette demande a déjà été validé par un⋅e animateur⋅rice ou gestionnaire du groupe."
        " Pour permettre sa transmission, elle doit encore être validée par un deuxième animateur⋅rice ou"
        " gestionnaire.",
        SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION: "Lorsque vous aurez intégré les modifications demandées, vous pourrez de nouveau"
        " transmettre cette demande à l'équipe de suivi.",
    },
    SpendingRequest.Status.TO_PAY: "L'allocation de votre groupe est maintenant suffisante pour permettre le paiement de"
    " cette demande.",
}

NEXT_STATUS_ACTION = {
    SpendingRequest.Status.AWAITING_PEER_REVIEW: "Valider",
    SpendingRequest.Status.AWAITING_ADMIN_REVIEW: "Transmettre",
    SpendingRequest.Status.PAID: "Demander le paiement",
}


def get_missing_field_error_message(spending_request):
    missing_fields = get_spending_request_field_labels(spending_request.missing_fields)

    if not missing_fields:
        return None

    message = ngettext(
        f"Le champ suivant est obligatoire pour la validation : {missing_fields[0]}.",
        f"Les champs suivants sont obligatoires pour la validation : {', '.join(missing_fields)}.",
        len(missing_fields),
    )

    return message


def get_status_explanation(spending_request, user):
    current_status = spending_request.status
    next_status = spending_request.next_status(user)

    if next_status and NEXT_STATUS_EXPLANATION.get(next_status, None):
        if isinstance(NEXT_STATUS_EXPLANATION[next_status], dict):
            if NEXT_STATUS_EXPLANATION[next_status].get(current_status, None):
                return NEXT_STATUS_EXPLANATION[next_status][current_status]
        else:
            return NEXT_STATUS_EXPLANATION[next_status]

    if STATUS_EXPLANATION.get(current_status, None):
        return STATUS_EXPLANATION[current_status]

    explanation = "Avant de pouvoir être envoyée pour validation, votre demande doit être complète."

    if not spending_request.missing_fields:
        return explanation

    return explanation + get_missing_field_error_message(spending_request)


def get_current_action(spending_request, user):
    next_status = spending_request.next_status(user)
    label = NEXT_STATUS_ACTION[next_status] if next_status else None
    return {
        "label": label,
        "explanation": get_status_explanation(spending_request, user),
    }


def validate_action(spending_request, user):
    """Valide la requête pour vérification pour l'administration, ou confirme la demande de paiement

    :param spending_request:
    :param user:
    :return: whether the spending request was successfully sent for review
    """
    next_status = spending_request.next_status(user)

    if not next_status:
        return False

    with reversion.create_revision(atomic=True):
        reversion.set_comment("Validation de la demande")
        reversion.set_user(user)

        spending_request.status = next_status
        spending_request.save()

        if spending_request.status == SpendingRequest.Status.TO_PAY:
            try:
                spending_request.operation = Spending.objects.create(
                    group=spending_request.group, amount=-spending_request.amount
                )
            except IntegrityError:
                return False

        if spending_request.status == SpendingRequest.Status.AWAITING_ADMIN_REVIEW:
            send_spending_request_to_review_email.delay(spending_request.pk)

        return True


def get_spending_request_field_label(field):
    if field in ("attachments", "documents"):
        return "Pièces-jointes"
    model_field = SpendingRequest._meta.get_field(field)
    return str(model_field.verbose_name if model_field else field)


def get_spending_request_field_labels(fields, join=False):
    fields = [get_spending_request_field_label(field) for field in fields]
    if not join:
        return fields
    return ", ".join(fields)
