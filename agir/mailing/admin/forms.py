from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm, CheckboxSelectMultiple


class SegmentAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["countries"].widget = FilteredSelectMultiple(
            "pays", False, choices=self.fields["countries"].choices
        )
        self.fields["departements"].widget = FilteredSelectMultiple(
            "départements", False, choices=self.fields["departements"].choices
        )

    class Meta:
        widgets = {
            "newsletters": CheckboxSelectMultiple,
            "person_qualification_status": CheckboxSelectMultiple,
        }
