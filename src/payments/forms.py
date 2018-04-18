import hmac
from django.core.exceptions import ValidationError
from hashlib import sha1

from django import forms
from django.conf import settings
from django.forms import fields


def get_signature(data):
    fields_names = list(data.keys())
    fields_names.sort()
    values = '+'.join([str(data[field_name]) for field_name in fields_names if field_name[0:5] == 'vads_'])
    values = values + '+' + settings.SYSTEMPAY_CERTIFICATE

    return sha1(values.encode('utf-8')).hexdigest()

class SystempayRedirectForm(forms.Form):
    vads_site_id = fields.IntegerField(initial=settings.SYSTEMPAY_SITE_ID, widget=forms.HiddenInput())
    vads_ctx_mode = fields.CharField(initial="PRODUCTION" if settings.SYSTEMPAY_PRODUCTION else "TEST", widget=forms.HiddenInput())
    vads_trans_id = fields.CharField(widget=forms.HiddenInput())
    vads_trans_date = fields.CharField(widget=forms.HiddenInput())
    vads_amount = fields.IntegerField(widget=forms.HiddenInput())
    vads_currency = fields.IntegerField(initial=settings.SYSTEMPAY_CURRENCY, widget=forms.HiddenInput())
    vads_action_mode = fields.CharField(initial="INTERACTIVE", widget=forms.HiddenInput())
    vads_page_action = fields.CharField(initial="PAYMENT", widget=forms.HiddenInput())
    vads_version = fields.CharField(initial="V2", widget=forms.HiddenInput())
    vads_payment_config = fields.CharField(initial="SINGLE", widget=forms.HiddenInput())
    vads_capture_delay = fields.IntegerField(initial=0, widget=forms.HiddenInput())
    vads_validation_mode = fields.IntegerField(initial=0, widget=forms.HiddenInput())
    vads_cust_email = fields.EmailField(widget=forms.HiddenInput())
    vads_cust_id = fields.UUIDField(widget=forms.HiddenInput())
    vads_cust_status = fields.CharField(initial="PRIVATE", widget=forms.HiddenInput())
    vads_cust_first_name = fields.CharField(widget=forms.HiddenInput())
    vads_cust_last_name = fields.CharField(widget=forms.HiddenInput())
    vads_cust_cell_address = fields.CharField(widget=forms.HiddenInput())
    vads_cust_zip = fields.CharField(widget=forms.HiddenInput())
    vads_cust_city = fields.CharField(widget=forms.HiddenInput())
    vads_cust_country = fields.CharField(widget=forms.HiddenInput())
    vads_ext_info_type = fields.CharField(widget=forms.HiddenInput())
    signature = fields.CharField(widget=forms.HiddenInput())

    def add_field(self, name, value):
        self.fields['name'] = forms.CharField(initial=value, widget=forms.HiddenInput())

    def update_signature(self):
        data = {field: str(self.get_initial_for_field(self.fields[field], field)) for field in self.fields.keys()}
        self.fields['signature'].initial = get_signature(data)
