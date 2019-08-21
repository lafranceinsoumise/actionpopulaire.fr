from agir.money.payment_mode import AbstractMoneyPaymentMode


class MoneyPaymentMode(AbstractMoneyPaymentMode):
    id = "money"
    url_fragment = "liquide"
    label = "Paiement sur place en liquide"
