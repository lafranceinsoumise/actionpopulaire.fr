from django.utils.translation import ugettext_lazy as _


class CenterOnFranceMixin:
    # for some reason it has to be in projected coordinates
    default_lon = 364043
    default_lat = 5850840
    default_zoom = 5


class DisplayContactPhoneMixin:
    def display_contact_phone(self, object):
        if object.contact_phone:
            return object.contact_phone.as_international
        return "-"
    display_contact_phone.short_description = _("Numéro de contact")
    display_contact_phone.admin_order_field = 'contact_phone'
