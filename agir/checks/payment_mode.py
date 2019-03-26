from django.utils.functional import cached_property

from agir.checks.views import CheckView
from ..payments.abstract_payment_mode import AbstractPaymentMode


class AbstractCheckPaymentMode(AbstractPaymentMode):
    can_retry = True
    can_cancel = True
    can_admin = True

    order = None
    address = None

    def __init__(self):
        self.view = CheckView.as_view(order=self.order, address=self.address)

    @cached_property
    def payment_view(self):
        return self.view

    @cached_property
    def retry_payment_view(self):
        return self.view
