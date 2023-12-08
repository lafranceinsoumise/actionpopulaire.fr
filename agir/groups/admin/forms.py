from django import forms
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from agir.groups.models import SupportGroupSubtype, Membership
from agir.lib.form_fields import AdminRichEditorWidget
from agir.lib.forms import CoordinatesFormMixin
from agir.people.models import Person
from .. import models
from ...lib.admin.form_fields import AutocompleteSelectModel


def subtype_label_from_instance(instance):
    return mark_safe(
        "<small>{}</small>&ensp;<strong>{}</strong>".format(
            instance.get_type_display().upper(),
            instance.label.capitalize(),
        )
    )


class SupportGroupAdminForm(CoordinatesFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_creation = self.instance._state.adding

        self.fields["subtypes"].label_from_instance = subtype_label_from_instance

        if self.is_creation:
            self.fields[
                "subtypes"
            ].queryset = SupportGroupSubtype.objects.active().order_by("-type")
        else:
            self.fields["subtypes"].queryset = (
                SupportGroupSubtype.objects.active()
                .filter(
                    Q(type=self.instance.type)
                    | Q(id__in=self.instance.subtypes.values_list("id", flat=True))
                )
                .order_by("-type")
            )

    class Meta:
        exclude = ("id", "members")
        widgets = {
            "description": AdminRichEditorWidget(),
            "tags": forms.CheckboxSelectMultiple(),
            "subtypes": forms.CheckboxSelectMultiple(),
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
        label=_("Statut"),
    )
    description = forms.CharField(required=False, label=_("Description"))

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
        membership = Membership(
            person=self.cleaned_data["person"],
            supportgroup=self.group,
            membership_type=self.cleaned_data["membership_type"],
        )

        if self.cleaned_data.get("description", None):
            membership.description = self.cleaned_data["description"].strip()

        membership.save()

        return membership
