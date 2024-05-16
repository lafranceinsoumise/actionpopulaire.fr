from agir.legacy.utils import LegacyPaymentType
from agir.payments.types import register_payment_type


register_payment_type(
    LegacyPaymentType(
        id="don_presidentielle2017",
        label="Don à la campagne présidentielle 2017",
        description_template="legacy/presidentielle2017/donation_description.html",
    )
)
