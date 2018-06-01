from collections import OrderedDict
from django.conf import settings
from django.utils.module_loading import import_string

__all__ = ['PAYMENT_MODES', 'DEFAULT_MODE']


_payment_classes = [import_string(name) for name in settings.PAYMENT_MODES]
PAYMENT_MODES = OrderedDict((klass.id, klass()) for klass in _payment_classes)
DEFAULT_MODE = _payment_classes[0].id
