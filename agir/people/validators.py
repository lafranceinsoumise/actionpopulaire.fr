from django.conf import settings
from django.core.validators import EmailValidator


class BlackListEmailValidator(EmailValidator):
    def validate_domain_part(self, domain_part):
        if domain_part in settings.EMAIL_DOMAIN_BLACKLIST:
            return False
        return super().validate_domain_part(domain_part)
