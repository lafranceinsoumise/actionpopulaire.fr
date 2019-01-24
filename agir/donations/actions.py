import reversion
from django.conf import settings
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from reversion.models import Version

from agir.donations.models import Operation, SpendingRequest, Document
from agir.lib.display import display_price


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


def summary(spending_request):
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

    if spending_request.status in spending_request.STATUS_NEED_ACTION:
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


def history(spending_request):
    versions = (
        Version.objects.get_for_object(spending_request)
        .order_by("pk")
        .select_related("revision__user__person")
    )

    diffed_fields = [
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

    current_fields = {}
    diff = {}

    for version in versions:
        fields = version.field_dict
        person = version.revision.user.person.get_short_name()
        modified = fields["modified"]

        if current_fields:
            diff = {
                get_spending_request_field_label(f)
                for f in diffed_fields
                if fields.get(f) != current_fields.get(f)
            }

        if fields["status"] == current_fields.get("status"):
            content = format_html(
                "<blockquote>{comment}</blockquote><p><em>Champs modifiés : {fields}</em>",
                comment=version.revision.get_comment(),
                fields=", ".join(diff),
            )

            yield {
                "title": "Modification de la demande",
                "user": person,
                "modified": modified,
                "content": content,
            }
        elif fields["status"] == spending_request.STATUS_DRAFT:
            yield {
                "title": "Création de la demande",
                "user": person,
                "modified": modified,
            }
        elif fields["status"] == spending_request.STATUS_AWAITING_GROUP_VALIDATION:
            yield {
                "title": "Validé par l'auteur d'origine",
                "user": person,
                "modified": modified,
            }
        elif fields["status"] == spending_request.STATUS_AWAITING_REVIEW:
            if (
                current_fields.get("status")
                == spending_request.STATUS_AWAITING_GROUP_VALIDATION
            ):
                yield {
                    "title": "Validé par un⋅e second⋅e animateur⋅rice",
                    "user": person,
                    "modified": modified,
                }
            else:
                yield {
                    "title": "Renvoyé pour validation à la Trésorerie",
                    "user": person,
                    "modified": modified,
                }
        else:
            yield {
                "title": "Modification non classée.",
                "user": person,
                "modified": modified,
            }

        current_fields = fields


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


def can_edit(spending_request):
    return spending_request.status in [
        SpendingRequest.STATUS_DRAFT,
        SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION,
        SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
        SpendingRequest.STATUS_AWAITING_REVIEW,
    ]


def can_send_for_review(spending_request, user):
    """Check if user can send spending_request for review

    :param spending_request: the spending_request to check
    :param user: the user that could send for review
    :return: boolean
    """

    # the spending_request cannot be sent for review if it is already under review, or the review has been done
    if spending_request.status not in SpendingRequest.STATUS_NEED_ACTION:
        return False

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


REVIEW_STATES_MAP = {
    SpendingRequest.STATUS_DRAFT: SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION,
    SpendingRequest.STATUS_AWAITING_GROUP_VALIDATION: SpendingRequest.STATUS_AWAITING_REVIEW,
    SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION: SpendingRequest.STATUS_AWAITING_REVIEW,
}


def send_for_review(spending_request, user):
    """Send spending request for review is user is allowed to

    :param spending_request:
    :param user:
    :return: whether the spending request was successfully sent for review
    """

    if spending_request.status not in REVIEW_STATES_MAP or not can_send_for_review(
        spending_request, user
    ):
        return False

    with reversion.create_revision():
        reversion.set_user(user)
        spending_request.status = REVIEW_STATES_MAP[spending_request.status]
        spending_request.save()

    return True
