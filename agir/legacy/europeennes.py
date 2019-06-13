from django.http import Http404

from agir.payments.types import register_payment_type, PaymentType


def not_found(request, payment):
    raise Http404()


register_payment_type(
    PaymentType(
        "don_europeennes",
        "Don à la campagne européenne 2019",
        not_found,
        description_template="legacy/europeennes/donation_description.html",
    )
)

register_payment_type(
    PaymentType(
        "pret_europeennes",
        "Prêt à la campagne européeenne 2019",
        not_found,
        description_template="legacy/europeennes/loan_description.html",
    )
)
