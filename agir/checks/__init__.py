from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from ..payments.abstract_payment_mode import AbstractPaymentMode


class CheckPaymentMode(AbstractPaymentMode):
    id = 'check'
    url_fragment = 'cheque'
    label =_('Paiement par chèque')

    can_retry = True

    @cached_property
    def payment_view(self):
        from . import views
        return views.CheckView.as_view()

    @cached_property
    def retry_payment_view(self):
        from . import views
        return views.CheckView.as_view()
