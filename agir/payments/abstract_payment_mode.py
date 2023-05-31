class AbstractPaymentMode:
    """A payment method can implement payments, subscriptions, or both."""

    can_retry = False
    can_cancel = False
    can_refund = False
    can_admin = False
    support_subscription = False

    @property
    def id(self):
        """L'identifiant du mode de paiement tel qu'il est notamment sauvegardé en base de données"""
        raise NotImplementedError(
            "Obligatoire pour tous les modes de paiement, même historiques."
        )

    @property
    def title(self):
        """Le titre long du mode de paiement, par exemple dans les emails récapitulatifs"""
        raise NotImplementedError(
            "Obligatoire pour tous les modes de paiement, même historiques."
        )

    @property
    def label(self):
        """Le libellé court du mode de paiement, par exemple dans les formulaires de choix du mode"""
        return self.title

    @property
    def category(self):
        """Un champ utilisé pour pouvoir regrouper plusieurs modes de paiement liés entre eux"""
        raise NotImplementedError("Must implement this property.")

    @property
    def url_fragment(self):
        return self.id

    @property
    def payment_view(self):
        raise NotImplementedError(
            "Cette propriété est obligatoire pour pouvoir réaliser de nouveaux paiements."
        )

    @property
    def subscription_view(self):
        raise NotImplementedError("Must implement this property.")

    def cancel_or_refund_payment_action(self, payment, *args, **kwargs):
        """
        Through this action, the payment must be cancelled and/or refunded.

        If the cancellation/refund is impossible, the PaymentMethod must raise
        an error.
        """
        raise NotImplementedError("Must implement this property")

    def subscription_terminate_action(self, subscription):
        """
        In this action, the payment method must delete any process
        of automatic payment in third party service, so the person
        won't be billed next period.

        If it is not possible to stop, the PaymentMethod must raise
        an error. This property must return a method.
        """
        raise NotImplementedError("Must implement this property")

    @staticmethod
    def get_urls():
        """Returns additional urls associated with this payment mode.

        :return:
        """
        return []
