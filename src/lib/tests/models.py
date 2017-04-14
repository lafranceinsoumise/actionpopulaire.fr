from .. import models


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
