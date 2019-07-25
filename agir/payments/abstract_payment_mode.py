class AbstractPaymentMode:
    """A payment method can implement payments, subscriptions, or both."""

    can_retry = False
    can_cancel = False
    can_admin = False
    support_subscription = False

    @property
    def id(self):
        raise NotImplementedError("Must implement this property.")

    @property
    def payment_view(self):
        raise NotImplementedError("Must implement this property.")

    @property
    def subscription_view(self):
        raise NotImplementedError("Must implement this property.")

    def subscription_terminate_action(self, subscription):
        """
        In this action, the payment method must delete any process
        of automatic payment in third party service, so the person
        won't be billed next period.

        If it is not possible to stop, the PaymentMethod must raise
        an error. This property must return a method.
        """
        raise NotImplementedError("Must implement this property")

    @property
    def category(self):
        raise NotImplementedError("Must implement this property.")

    @property
    def url_fragment(self):
        return self.id

    @staticmethod
    def get_urls():
        """Returns additional urls associated with this payment mode.

        :return:
        """
        return []
