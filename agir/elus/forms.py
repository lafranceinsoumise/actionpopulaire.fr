from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.contrib.postgres.forms import DateRangeField

from agir.elus.models import (
    MandatMunicipal,
    STATUT_A_VERIFIER_INSCRIPTION,
    MUNICIPAL_DEFAULT_DATE_RANGE,
    DELEGATIONS_CHOICES,
    STATUT_A_VERIFIER_IMPORT,
    STATUT_A_VERIFIER_ADMIN,
)
from agir.lib.form_fields import CommuneField
from agir.people.models import Person


class BaseMandatForm(forms.ModelForm):
    class Meta:
        fields = ("dates", "mandat")


class MandatMunicipalForm(BaseMandatForm):
    dates = DateRangeField(
        label="Dates de votre mandat",
        required=True,
        initial=MUNICIPAL_DEFAULT_DATE_RANGE,
        help_text="Indiquez la date de votre entrée au conseil municipal, et la date approximative à laquelle votre"
        " mandat devrait se finir (à moins que vous n'ayiez déjà démissionné.",
    )

    membre_reseau_elus = forms.ChoiceField(
        label="Souhaitez-vous faire partie du réseau des élu⋅es ?",
        choices=(
            (Person.MEMBRE_RESEAU_SOUHAITE, "Oui"),
            (Person.MEMBRE_RESEAU_NON, "Non"),
        ),
        required=True,
    )

    delegations = forms.MultipleChoiceField(
        label="Si vous êtes maire adjoint⋅e ou vice-président⋅e de l'EPCI, indiquez dans quels domains rentrent vos"
        " délégations.",
        choices=DELEGATIONS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, person, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance.person = person

        self.fields["mandat"].choices = [
            ("", "Indiquez votre situation au conseil municipal")
        ] + [
            c
            for c in self.fields["mandat"].choices
            if c[0] != MandatMunicipal.MANDAT_INCONNU
        ]
        self.fields["communautaire"].choices = [
            c
            for c in self.fields["communautaire"].choices
            if c[0] != MandatMunicipal.MANDAT_EPCI_MANDAT_INCONNU
        ]

        if person.membre_reseau_elus == Person.MEMBRE_RESEAU_NON:
            self.fields["membre_reseau_elus"].initial = Person.MEMBRE_RESEAU_NON
        elif person.membre_reseau_elus != Person.MEMBRE_RESEAU_INCONNU:
            del self.fields["membre_reseau_elus"]

        if self.instance.conseil_id is not None:
            if self.instance.conseil.epci:
                self.fields[
                    "communautaire"
                ].label = f"Élu⋅e à la {self.instance.conseil.epci.nom}"
            else:
                del self.fields["communautaire"]

        self.helper = FormHelper()
        self.helper.layout = Layout("mandat", "communautaire", "dates", "delegations")
        if "membre_reseau_elus" in self.fields:
            self.helper.layout.fields.insert(2, "membre_reseau_elus")

        self.helper.add_input(Submit("valider", "Valider"))

    def save(self, commit=True):
        if self.instance.statut in [STATUT_A_VERIFIER_ADMIN, STATUT_A_VERIFIER_IMPORT]:
            self.instance.statut = STATUT_A_VERIFIER_INSCRIPTION

        if "membre_reseau_elus" in self.fields:
            self.instance.person.membre_reseau_elus = self.cleaned_data[
                "membre_reseau_elus"
            ]
            self.instance.person.save(update_fields=["membre_reseau_elus"])

        return super().save(commit=commit)

    class Meta:
        model = MandatMunicipal
        fields = BaseMandatForm.Meta.fields + ("communautaire", "delegations",)


class CreerMandatMunicipalForm(MandatMunicipalForm):
    conseil = CommuneField(types=["COM", "SRM"], label="Commune")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout.fields.insert(0, "conseil")

    class Meta(MandatMunicipalForm.Meta):
        fields = ("conseil",) + MandatMunicipalForm.Meta.fields
