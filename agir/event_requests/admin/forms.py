from django import forms

from agir.event_requests import models
from agir.lib.form_fields import MultiDateTimeField


class EventRequestAdminForm(forms.ModelForm):
    datetimes = MultiDateTimeField()

    class Meta:
        model = models.EventRequest
        fields = "__all__"


EventAssetTemplateFormSet = forms.modelformset_factory(
    model=models.EventAssetTemplate, fields="__all__"
)


class EventAssetTemplateForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_asset_template_formset = EventAssetTemplateFormSet(
            instance=self.instance, data=self.data or None, prefix=self.prefix
        )

    def is_valid(self):
        return super().is_valid() and self.event_asset_template_formset.is_valid()

    def save(self, commit=False):
        self.instance.eventassettemplate = self.event_asset_template_formset.save()
        return super().save(commit=commit)
