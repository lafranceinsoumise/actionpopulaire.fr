from agir.payments.abstract_payment_mode import AbstractPaymentMode


class ImportedPaymentMode(AbstractPaymentMode):
    """
    Utilisé pour les paiements réalisés dans une autre application, mais importé pour
    pouvoir être référencé dans le profil des personnes.

    Ne doit pas être utilisé pour effectuer de nouveaux paiements.
    """

    id = "imported"
    category = "imported"
    title = "Paiement importé depuis un autre système de paiement"
