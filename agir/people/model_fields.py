from django.contrib.postgres.fields import JSONField

from . import form_fields

class MandatesField(JSONField):
    def formfield(self, **kwargs):
        defaults = {'form_class': form_fields.MandatesField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
