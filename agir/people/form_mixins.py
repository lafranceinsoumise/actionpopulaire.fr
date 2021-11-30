__all__ = []


class ContactPhoneNumberMixin:
    """Solves a bug in phonenumbers_fields when field is missing from POSTed data"""

    def clean_contact_phone(self):
        contact_phone = self.cleaned_data.get("contact_phone")

        if contact_phone is None:
            contact_phone = ""

        return contact_phone
