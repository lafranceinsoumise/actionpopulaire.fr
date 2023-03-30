from django import forms
from django.utils.translation import gettext_lazy as _

from agir.groups.models import SupportGroupSubtype, SupportGroup, Membership
from agir.lib.form_fields import AdminRichEditorWidget
from agir.lib.forms import CoordinatesFormMixin
from agir.people.models import Person
from .. import models
from ...lib.admin.form_fields import AutocompleteSelectModel


class SupportGroupAdminForm(CoordinatesFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.is_creation = self.instance._state.adding
        # if self.is_creation:
        #     self.fields[
        #         "subtypes"
        #     ].label_from_instance = lambda instance: "{} ({})".format(
        #         instance.label, dict(SupportGroup.TYPE_CHOICES)[instance.type]
        #     )
        # else:
        #     self.fields["subtypes"].queryset = SupportGroupSubtype.objects.filter(
        #         type=self.instance.type
        #     )

    class Meta:
        exclude = ("id", "members")
        widgets = {
            "description": AdminRichEditorWidget(),
            "tags": forms.CheckboxSelectMultiple(),
        }


class AddMemberForm(forms.Form):
    person = forms.ModelChoiceField(
        Person.objects.all(), required=True, label=_("Personne à ajouter")
    )
    membership_type = forms.ChoiceField(
        choices=(
            choice
            for choice in Membership.MEMBERSHIP_TYPE_CHOICES
            if choice[0] <= Membership.MEMBERSHIP_TYPE_MEMBER
        ),
        initial=Membership.MEMBERSHIP_TYPE_MEMBER,
        widget=forms.RadioSelect,
        required=True,
        label="Statut",
    )

    def __init__(self, group, model_admin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.fields["person"].widget = AutocompleteSelectModel(
            Person,
            admin_site=model_admin.admin_site,
            choices=self.fields["person"].choices,
        )

    def clean_person(self):
        person = self.cleaned_data["person"]
        if models.Membership.objects.filter(
            person=person, supportgroup=self.group
        ).exists():
            raise forms.ValidationError(_("Cette personne fait déjà partie du groupe"))

        return person

    def save(self):
        return models.Membership.objects.create(
            person=self.cleaned_data["person"],
            supportgroup=self.group,
            membership_type=self.cleaned_data["membership_type"],
        )
