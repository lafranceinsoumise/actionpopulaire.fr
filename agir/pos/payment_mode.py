from django.utils.functional import cached_property
from django.views.defaults import page_not_found

from ..payments.abstract_payment_mode import AbstractPaymentMode


class AbstractPOSPaymentMode(AbstractPaymentMode):
    can_retry = True
    can_cancel = True
    can_admin = True

    def __init__(self):
        self.view = page_not_found

    @cached_property
    def payment_view(self):
        return self.view

    @cached_property
    def retry_payment_view(self):
        return self.view


class AbstractMoneyPaymentMode(AbstractPOSPaymentMode):
    title = "Votre paiement en liquide"
    category = "money"


class AbstractTPEPaymentMode(AbstractPOSPaymentMode):
    title = "Votre paiement par carte"
    category = "tpe"
