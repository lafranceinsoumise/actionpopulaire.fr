from datetime import datetime

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import phonenumberutil, PhoneNumberType

from lib.models import LocationMixin
from .forms import SystempayRedirectForm
from .types import get_payment_choices


class Payment(TimeStampedModel, LocationMixin):
    STATUS_WAITING = 0
    STATUS_COMPLETED = 1
    STATUS_ABANDONED = 2
    STATUS_CANCELED = 3
    STATUS_REFUSED = 4

    STATUS_CHOICES = (
        (STATUS_WAITING, 'En attente'),
        (STATUS_COMPLETED, 'Terminé'),
        (STATUS_ABANDONED, 'Abandonné'),
        (STATUS_CANCELED, 'Annulé'),
        (STATUS_REFUSED, 'Refusé')
    )

    person = models.ForeignKey('people.Person')

    email = models.EmailField('email', max_length=255)
    first_name = models.CharField('prénom', max_length=255)
    last_name = models.CharField('nom de famille', max_length=255)
    phone_number = PhoneNumberField('numéro de téléphone', null=True)

    type = models.CharField("type", choices=get_payment_choices(), max_length=255)
    price = models.IntegerField("prix en centimes d'euros")
    status = models.IntegerField("status", choices=STATUS_CHOICES, default=STATUS_WAITING)
    meta = JSONField(blank=True, default=dict)
    systempay_responses = JSONField(blank=True, default=list)

    def get_form(self):
        form = SystempayRedirectForm(initial={
            'vads_trans_id': str(self.pk % 900000).zfill(6),
            'vads_trans_date': datetime.utcnow().strftime('%Y%m%d%H%M%S'),
            'vads_amount': self.price,
            'vads_cust_email': self.email,
            'vads_cust_id': str(self.person.id),
            'vads_cust_first_name': self.first_name,
            'vads_cust_last_name': self.last_name,
            'vads_cust_address': ', '.join([self.location_address1, self.location_address2]),
            'vads_cust_zip': self.location_zip,
            'vads_cust_city': self.location_city,
            'vads_cust_state': self.location_state,
            'vads_cust_country': self.location_country,
            'vads_ext_info_type': self.type
        })

        if self.phone_number:
            if phonenumberutil.number_type(self.phone_number) == PhoneNumberType.MOBILE:
                form.add_field('vads_cust_cell_phone', self.phone_number.as_e164)
            else:
                form.add_field('vads_cust_phone', self.phone_number.as_e164)

        for key in self.meta:
            form.add_field('vads_ext_info_meta_' + key, self.meta[key])

        form.update_signature()

        return form


    def get_form_action(self):
        return 'https://paiement.systempay.fr/vads-payment/'

    def get_payment_url(self):
        return reverse('payment_redirect', args=[self.pk])
