from django.db.models import Model

from .. import models
from agir.lib.model_fields import IBANField


class UUIDModel(models.UUIDIdentified):
    pass


class NBModel(models.NationBuilderResource):
    pass


class LocationModel(models.LocationMixin):
    pass


class ContactModel(models.ContactMixin):
    pass


class APIResource(models.BaseAPIResource):
    pass


class Label(models.AbstractLabel):
    pass


class IBANTestModel(Model):
    iban = IBANField("IBAN")
