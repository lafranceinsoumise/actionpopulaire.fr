from agir.pos.payment_mode import AbstractMoneyPaymentMode, AbstractTPEPaymentMode


class MoneyPaymentMode(AbstractMoneyPaymentMode):
    id = "money"
    url_fragment = "liquide"
    label = "Paiement sur place en liquide"


class TPEPaymentMode(AbstractTPEPaymentMode):
    id = "tpe"
    url_fragment = "tpe"
    label = "Paiement sur place par carte bleue"
