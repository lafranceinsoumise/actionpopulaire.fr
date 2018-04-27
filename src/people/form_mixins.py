from django import forms

__all__ = ['MetaFieldsMixin']


class MetaFieldsMixin(forms.Form):
    meta_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in self.get_meta_fields():
            self.initial[f] = self.instance.meta.get(f)

    def get_meta_fields(self):
        return self.meta_fields

    def clean(self):
        """Handles meta fields"""
        cleaned_data = super().clean()

        meta_update = {f: cleaned_data.get(f) for f in self.get_meta_fields() if cleaned_data.get(f)}
        self.instance.meta.update(meta_update)

        return cleaned_data
