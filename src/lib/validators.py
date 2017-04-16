from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import ValidationError


class MaxLengthValidator():
    def __init__(self, max_length):
        self.max_length = max_length

    def __call__(self, value):
        if len(value) > self.max_length:
            message = _('Ce champ a une longueur maximale de {max_length').format(max_length=self.max_length)
            raise ValidationError(message)

