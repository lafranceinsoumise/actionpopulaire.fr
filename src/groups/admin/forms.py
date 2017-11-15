from django import forms
from django.utils.translation import ugettext_lazy as _

from ajax_select.fields import AutoCompleteSelectField

from lib.forms import CoordinatesFormMixin
from lib.form_fields import AdminRichEditorWidget

from .. import models


class SupportGroupAdminForm(CoordinatesFormMixin, forms.ModelForm):
    class Meta:
        exclude = (
            'id', 'members'
        )
        widgets = {'description': AdminRichEditorWidget()}


class AddMemberForm(forms.Form):
    person = AutoCompleteSelectField(
        "people",
        required=True,
        label=_("Personne à ajouter"),
        help_text=""
    )

    def __init__(self, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group

    def clean_person(self):
        person = self.cleaned_data['person']
        if models.Membership.objects.filter(person=person, supportgroup=self.group).exists():
            raise forms.ValidationError(_("Cette personne fait déjà partie du groupe"))

        return person

    def save(self):
        return models.Membership.objects.create(person=self.cleaned_data['person'], supportgroup=self.group)
