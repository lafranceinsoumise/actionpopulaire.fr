from collections import OrderedDict
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from django.forms import ChoiceField, Field, RadioSelect

__all__ = ["PAYMENT_MODES", "DEFAULT_MODE"]


_payment_classes = [import_string(name) for name in settings.PAYMENT_MODES]
PAYMENT_MODES = OrderedDict((klass.id, klass()) for klass in _payment_classes)
DEFAULT_MODE = _payment_classes[0].id


class PaymentModeField(ChoiceField):
    widget = RadioSelect

    def __init__(
        self,
        *,
        payment_modes=None,
        empty_label=_("Choisissez votre moyen de paiement"),
        required=True,
        initial=None,
        label=_("Mode de paiement"),
        **kwargs
    ):
        self._payment_modes = (
            payment_modes if payment_modes is not None else list(PAYMENT_MODES.values())
        )

        if required:
            self.empty_label = None
        else:
            self.empty_label = empty_label

        # bypassing ChoiceField constructor, see ModelChoiceField implementation for reference
        Field.__init__(self, required=required, label=label, initial=initial, **kwargs)
        self.widget.choices = self.choices

    @property
    def payment_modes(self):
        return self._payment_modes

    @payment_modes.setter
    def payment_modes(self, value):
        self._payment_modes = value
        self.widget.choices = self.choices

    @property
    def choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, "_choices"):
            return self._choices

        # Otherwise, execute the QuerySet in self.queryset to determine the
        # choices dynamically. Return a fresh ModelChoiceIterator that has not been
        # consumed. Note that we're instantiating a new ModelChoiceIterator *each*
        # time _get_choices() is called (and, thus, each time self.choices is
        # accessed) so that we can ensure the QuerySet has not been consumed. This
        # construct might look complicated but it allows for lazy evaluation of
        # the queryset.
        return [(p.id, p.label) for p in self._payment_modes]

    choices.setter(ChoiceField._set_choices)

    def prepare_value(self, value):
        if hasattr(value, "id"):
            return value.id
        return super().prepare_value(value)

    def to_python(self, value):
        if value in self.empty_values:
            return None

        if value in PAYMENT_MODES:
            return PAYMENT_MODES[value]

        raise ValidationError(
            self.error_messages["invalid_choice"], code="invalid_choice"
        )

    def validate(self, value):
        return Field.validate(self, value)

    def has_changed(self, initial, data):
        if self.disabled:
            return False
        initial_value = initial if initial is not None else ""
        data_value = data if data is not None else ""
        return str(self.prepare_value(initial_value)) != str(data_value)

    def __deepcopy__(self, memo):
        # bypass ChoiceField __deepcopy__
        return super(ChoiceField, self).__deepcopy__(memo)
