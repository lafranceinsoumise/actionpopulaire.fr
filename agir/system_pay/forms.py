from django import forms
from django.forms import fields
from phonenumbers import phonenumberutil, PhoneNumberType

from agir.lib.utils import front_url_lazy, front_url
from agir.system_pay.utils import (
    get_trans_id_from_order_id,
    get_recurrence_rule,
)
from . import SystemPayConfig
from .crypto import get_signature


class SystempayBaseForm(forms.Form):
    form_action = "https://paiement.systempay.fr/vads-payment/"

    vads_site_id = fields.IntegerField(widget=forms.HiddenInput())
    vads_ctx_mode = fields.CharField(widget=forms.HiddenInput())
    vads_action_mode = fields.CharField(
        initial="INTERACTIVE", widget=forms.HiddenInput()
    )
    vads_version = fields.CharField(initial="V2", widget=forms.HiddenInput())

    vads_order_id = fields.CharField(widget=forms.HiddenInput())
    vads_trans_id = fields.CharField(widget=forms.HiddenInput())
    vads_trans_date = fields.CharField(widget=forms.HiddenInput())

    vads_url_cancel = fields.CharField(
        initial=front_url_lazy("system_pay:return", query={"status": "cancel"}),
        widget=forms.HiddenInput(),
    )
    vads_url_error = fields.CharField(
        initial=front_url_lazy("system_pay:return", query={"status": "error"}),
        widget=forms.HiddenInput(),
    )
    vads_url_refused = fields.CharField(
        initial=front_url_lazy("system_pay:return", query={"status": "refused"}),
        widget=forms.HiddenInput(),
    )
    vads_url_success = fields.CharField(
        initial=front_url_lazy("system_pay:return", query={"status": "success"}),
        widget=forms.HiddenInput(),
    )
    vads_redirect_success_timeout = fields.CharField(
        initial=8, widget=forms.HiddenInput()
    )
    vads_redirect_error_timeout = fields.CharField(
        initial=8, widget=forms.HiddenInput()
    )

    vads_cust_email = fields.EmailField(widget=forms.HiddenInput())
    vads_cust_id = fields.UUIDField(widget=forms.HiddenInput())
    vads_cust_status = fields.CharField(initial="PRIVATE", widget=forms.HiddenInput())
    vads_cust_first_name = fields.CharField(widget=forms.HiddenInput())
    vads_cust_last_name = fields.CharField(widget=forms.HiddenInput())
    vads_cust_address = fields.CharField(widget=forms.HiddenInput())
    vads_cust_zip = fields.CharField(widget=forms.HiddenInput())
    vads_cust_city = fields.CharField(widget=forms.HiddenInput())
    vads_cust_country = fields.CharField(widget=forms.HiddenInput())
    vads_cust_state = fields.CharField(widget=forms.HiddenInput())

    signature = fields.CharField(widget=forms.HiddenInput())

    def add_field(self, name, value):
        if value is None:
            return
        self.fields[name] = forms.CharField(initial=value, widget=forms.HiddenInput())

    def update_signature(self, certificate):
        data = {
            field: str(self.get_initial_for_field(self.fields[field], field))
            for field in self.fields.keys()
        }
        self.fields["signature"].initial = get_signature(data, certificate)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # SystemPay a des maximums de longueur pour chacun des ces champs
        trans_table = str.maketrans("", "", "<>")
        for f, l in {
            "vads_cust_first_name": 63,
            "vads_cust_last_name": 63,
            "vads_cust_address": 255,
            "vads_cust_zip": 64,
            "vads_cust_city": 128,
            "vads_cust_state": 127,
        }.items():
            if self.get_initial_for_field(self.fields[f], f):
                self.initial[f] = self.get_initial_for_field(
                    self.fields[f], f
                ).translate(trans_table)[:l]


class SystempayNewSubscriptionForm(SystempayBaseForm):
    vads_page_action = fields.CharField(
        initial="REGISTER_SUBSCRIBE", widget=forms.HiddenInput()
    )
    vads_sub_amount = fields.IntegerField(widget=forms.HiddenInput())
    vads_sub_effect_date = fields.CharField(widget=forms.HiddenInput())
    vads_sub_currency = fields.IntegerField(widget=forms.HiddenInput())
    vads_sub_desc = fields.CharField(widget=forms.HiddenInput())

    @classmethod
    def get_form_for_transaction(cls, transaction, sp_config: SystemPayConfig):
        person = transaction.subscription.person

        success_url = front_url(
            "subscription_return", kwargs={"pk": transaction.subscription_id}
        )
        failure_url = front_url(
            f"{transaction.subscription.mode}:failure", kwargs={"pk": transaction.pk}
        )

        person_data = {}
        if person is not None:
            person_data.update(
                {
                    f.name: getattr(person, f.name)
                    for f in person._meta.get_fields()
                    if not f.is_relation
                }
            )
        person_data.update(transaction.subscription.meta)

        effect_date = (
            transaction.subscription.effect_date
            if transaction.subscription.effect_date
            else transaction.created
        )

        form = cls(
            initial={
                "vads_site_id": sp_config.site_id,
                "vads_ctx_mode": "PRODUCTION" if sp_config.production else "TEST",
                "vads_sub_currency": sp_config.currency,
                "vads_order_id": transaction.pk,
                "vads_trans_id": get_trans_id_from_order_id(transaction.pk),
                "vads_trans_date": transaction.created.strftime("%Y%m%d%H%M%S"),
                "vads_sub_effect_date": effect_date.strftime("%Y%m%d"),
                "vads_sub_amount": transaction.subscription.price,
                "vads_cust_email": person.email,
                "vads_cust_id": transaction.subscription.person_id,
                "vads_cust_first_name": person_data.get("first_name"),
                "vads_cust_last_name": person_data.get("last_name"),
                "vads_cust_address": ", ".join(
                    [
                        person_data.get("location_address1", ""),
                        person_data.get("location_address2", ""),
                    ]
                ).strip(),
                "vads_cust_zip": person_data.get("location_zip"),
                "vads_cust_city": person_data.get("location_city"),
                "vads_cust_state": person_data.get("location_state"),
                "vads_cust_country": person_data.get("location_country"),
                "vads_sub_desc": get_recurrence_rule(transaction.subscription),
                "vads_url_success": success_url,
                **{
                    f"vads_url_{status}": f"{failure_url}?status={status}"
                    for status in ["cancel", "error", "refused"]
                },
            }
        )

        form.update_signature(sp_config.certificate)

        return form


class SystempayPaymentForm(SystempayBaseForm):
    vads_amount = fields.IntegerField(widget=forms.HiddenInput())
    vads_currency = fields.IntegerField(widget=forms.HiddenInput())
    vads_ext_info_type = fields.CharField(widget=forms.HiddenInput())

    vads_page_action = fields.CharField(initial="PAYMENT", widget=forms.HiddenInput())
    vads_payment_config = fields.CharField(initial="SINGLE", widget=forms.HiddenInput())
    vads_capture_delay = fields.IntegerField(initial=0, widget=forms.HiddenInput())
    vads_validation_mode = fields.IntegerField(initial=0, widget=forms.HiddenInput())

    @classmethod
    def get_form_for_transaction(cls, transaction, sp_config):
        person_id = (
            str(transaction.payment.person.pk)
            if transaction.payment.person
            else "anonymous"
        )

        success_url = front_url("payment_return", kwargs={"pk": transaction.payment_id})
        failure_url = front_url(
            f"{transaction.payment.mode}:failure", kwargs={"pk": transaction.pk}
        )

        form = cls(
            initial={
                "vads_site_id": sp_config.site_id,
                "vads_ctx_mode": "PRODUCTION" if sp_config.production else "TEST",
                "vads_currency": sp_config.currency,
                "vads_order_id": transaction.pk,
                "vads_trans_id": get_trans_id_from_order_id(transaction.pk),
                "vads_trans_date": transaction.created.strftime("%Y%m%d%H%M%S"),
                "vads_amount": transaction.payment.price,
                "vads_cust_email": transaction.payment.email,
                "vads_cust_id": person_id,
                "vads_cust_first_name": transaction.payment.first_name,
                "vads_cust_last_name": transaction.payment.last_name,
                "vads_cust_address": ", ".join(
                    [
                        transaction.payment.location_address1,
                        transaction.payment.location_address2,
                    ]
                ),
                "vads_cust_zip": transaction.payment.location_zip,
                "vads_cust_city": transaction.payment.location_city,
                "vads_cust_state": transaction.payment.location_state,
                "vads_cust_country": transaction.payment.location_country,
                "vads_ext_info_type": transaction.payment.type,
                "vads_url_success": success_url,
                **{
                    f"vads_url_{status}": f"{failure_url}?status={status}"
                    for status in ["cancel", "error", "refused"]
                },
            }
        )

        if transaction.payment.phone_number:
            if (
                phonenumberutil.number_type(transaction.payment.phone_number)
                == PhoneNumberType.MOBILE
            ):
                form.add_field(
                    "vads_cust_cell_phone", transaction.payment.phone_number.as_e164
                )
            else:
                form.add_field(
                    "vads_cust_phone", transaction.payment.phone_number.as_e164
                )

        for key in transaction.payment.meta:
            form.add_field("vads_ext_info_meta_" + key, transaction.payment.meta[key])

        form.update_signature(sp_config.certificate)

        return form
