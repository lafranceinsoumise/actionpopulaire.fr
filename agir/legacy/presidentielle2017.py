from django.http import Http404

from agir.payments.types import register_payment_type, PaymentType


def not_found(request, payment):
    raise Http404()


register_payment_type(
    PaymentType(
        "don_presidentielle2017",
        "Don à la campagne présidentielle 2017",
        not_found,
        description_template="legacy/europeennes/donation_description.html",
    )
)
