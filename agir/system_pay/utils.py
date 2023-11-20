import datetime
from typing import Mapping

SENSITIVE_FIELDS = {
    "vads_bank_code",
    "vads_bank_label",
    "vads_card_brand",
    "vads_card_number",
    "vads_threeds_eci",
    "vads_threeds_xid",
    "vads_bank_product",
    "vads_card_country",
    "vads_threeds_cavv",
    "vads_brand_management",
    "vads_threeds_enrolled",
    "vads_threeds_sign_valid",
    "vads_payment_certificate",
    "vads_threeds_cavvAlgorithm",
}


def get_trans_id_from_order_id(order_id):
    """Generate the transaction id for a SystemPay transaction from the order id

    :param order_id:
    :return:
    """
    return str(int(order_id) % 900000).zfill(6)


def clean_system_pay_data(data: Mapping[str, str]):
    return {k: v for k, v in data.items() if k not in SENSITIVE_FIELDS}


def get_recurrence_rule(subscription):
    if subscription.month_of_year is None:
        rule = f"RRULE:FREQ=MONTHLY;BYMONTHDAY={subscription.day_of_month}"
    else:
        rule = f"RRULE:FREQ=YEARLY;BYMONTH={subscription.month_of_year};BYMONTHDAY={subscription.day_of_month}"

    end_date = subscription.end_date
    if end_date and isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    if isinstance(end_date, datetime.date):
        rule = f"{rule};UNTIL={end_date.strftime('%Y%m%d')}"

    return rule
