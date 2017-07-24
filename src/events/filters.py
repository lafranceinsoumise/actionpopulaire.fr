from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
import django_filters

from .models import Calendar


class CalendarField(forms.Field):
    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            return Calendar.objects.get(label=value)
        except Calendar.DoesNotExist:
            raise ValidationError(_("Ce calendrier n'existe pas"))


class CalendarFilter(django_filters.Filter):
    field_class = CalendarField
