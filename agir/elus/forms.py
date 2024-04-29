from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from data_france.models import (
    CollectiviteDepartementale,
    CollectiviteRegionale,
    CirconscriptionConsulaire,
)
from django import forms
from django.contrib.postgres.forms import DateRangeField
from django.core.exceptions import NON_FIELD_ERRORS

from agir.elus.models import (
    MandatMunicipal,
    DELEGATIONS_CHOICES,
    MandatDepartemental,
    MandatRegional,
    MandatConsulaire,
    StatutMandat,
)
from agir.lib.form_fields import CommuneField
from agir.people.models import Person


class BaseMandatForm(forms.ModelForm):
    membre_reseau_elus = forms.ChoiceField(
        label="Souhaitez-vous faire partie du réseau des élu⋅es ?",
        choices=(
            (Person.MEMBRE_RESEAU_SOUHAITE, "Oui"),
            (Person.MEMBRE_RESEAU_NON, "Non"),
        ),
        required=True,
    )

    dates = DateRangeField(
        label="Dates de votre mandat",
        required=True,
        help_text="Indiquez la date de votre entrée au conseil, et la date approximative à laquelle votre"
        " mandat devrait se finir (à moins que votre mandat ne se soit déjà terminé).",
    )

    def __init__(self, *args, person, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance.person = person

        self.fields["dates"].initial = self.instance._meta.get_field("dates").default

        if person.membre_reseau_elus == Person.MEMBRE_RESEAU_NON:
            self.fields["membre_reseau_elus"].initial = Person.MEMBRE_RESEAU_NON
        elif person.membre_reseau_elus != Person.MEMBRE_RESEAU_INCONNU:
            del self.fields["membre_reseau_elus"]

        self.helper = FormHelper()
        self.helper.add_input(Submit("valider", "Valider"))
        self.helper.layout = Layout("conseil", "mandat", "dates")
        if "membre_reseau_elus" in self.fields:
            self.helper.layout.fields.insert(0, "membre_reseau_elus")

    def save(self, commit=True):
        if self.instance.statut in [
            StatutMandat.CONTACT_NECESSAIRE,
            StatutMandat.IMPORT_AUTOMATIQUE,
        ]:
            self.instance.statut = StatutMandat.INSCRIPTION_VIA_PROFIL

        if "membre_reseau_elus" in self.fields:
            self.instance.person.membre_reseau_elus = self.cleaned_data[
                "membre_reseau_elus"
            ]
            self.instance.person.save(update_fields=["membre_reseau_elus"])

        return super().save(commit=commit)

    class Meta:
        fields = ("conseil", "dates", "mandat")
        error_messages = {
            NON_FIELD_ERRORS: {
                "dates_overlap": "Vous avez déjà indiqué un autre mandat pour ce conseil à des dates qui se"
                " chevauchent. Modifiez plutôt cet autre mandat."
            }
        }


class AvecDelegationMixin(forms.Form):
    delegations = forms.MultipleChoiceField(
        label="Si vous êtes vice-président⋅e, indiquez dans quels domains rentrent vos"
        " délégations.",
        choices=DELEGATIONS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout.fields.append("delegations")


class MandatMunicipalForm(AvecDelegationMixin, BaseMandatForm):
    conseil = CommuneField(types=["COM", "SRM"], label="Commune")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["delegations"].help_text = (
            "Si vous êtes maire adjoint⋅e ou vice-président⋅e de l'EPCI, indiquez dans quels domaines rentrent vos"
            " délégations."
        )

        self.fields["communautaire"].choices = [
            (None, "Indiquez si vous êtes délégué⋅e à l'intercommunalité")
        ] + [
            c
            for c in self.fields["communautaire"].choices
            if c[0] != MandatMunicipal.MANDAT_EPCI_MANDAT_INCONNU
        ]

        if self.instance.conseil_id is not None:
            if self.instance.conseil.epci:
                self.fields["communautaire"].label = (
                    f"Élu⋅e à la {self.instance.conseil.epci.nom}"
                )
            else:
                del self.fields["communautaire"]

        self.helper.layout = Layout(
            "conseil", "mandat", "communautaire", "dates", "delegations"
        )
        if "membre_reseau_elus" in self.fields:
            self.helper.layout.fields.insert(2, "membre_reseau_elus")

    class Meta(BaseMandatForm.Meta):
        model = MandatMunicipal
        fields = BaseMandatForm.Meta.fields + (
            "communautaire",
            "delegations",
        )


class MandatDepartementalForm(AvecDelegationMixin, BaseMandatForm):
    # La Corse, la Martinique et la Guyane ont des collectivités uniques, et leurs conseillers sont élus simultanément
    # aux régionales, et selon des modalités proches. On empêche de créer des conseillers départementaux du coup.
    # Idem pour Paris dont les conseillers sont élus aux municipales.
    conseil = forms.ModelChoiceField(
        queryset=CollectiviteDepartementale.objects.exclude(
            code__in=["20R", "75C", "972R", "973R"]
        ),
        label="Département ou métropole",
        empty_label="Choisissez la collectivité",
        required=True,
    )

    class Meta(BaseMandatForm.Meta):
        model = MandatDepartemental
        fields = BaseMandatForm.Meta.fields + ("delegations",)


class MandatRegionalForm(AvecDelegationMixin, BaseMandatForm):
    # Mayotte a des compétences régionales mais les conseillers sont élus par canton,
    # comme des conseillers départementaux classiques.
    conseil = forms.ModelChoiceField(
        queryset=CollectiviteRegionale.objects.exclude(code="976R"),
        label="Région ou collectivité unique",
        empty_label="Choisissez la collectivité",
        required=True,
    )

    class Meta(BaseMandatForm.Meta):
        model = MandatRegional
        fields = BaseMandatForm.Meta.fields + ("delegations",)


class MandatConsulaireForm(BaseMandatForm):
    conseil = forms.ModelChoiceField(
        CirconscriptionConsulaire.objects.all(),
        label="Circonscription consulaire",
        empty_label="Indiquez la circonscription consulaire",
        required=True,
    )

    class Meta(BaseMandatForm.Meta):
        model = MandatConsulaire


class DemandeAccesApplicationParrainagesForm(forms.ModelForm):
    engagement = forms.BooleanField(
        required=True,
        label="Je m'engage à respecter les consignes données dans mes approches avec les élu·es susceptibles de"
        " parrainer la candidature de JLM.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in self.fields:
            self.fields[f].required = True

        self.helper = FormHelper()
        self.helper.add_input(Submit("valider", "Valider"))

    class Meta:
        model = Person
        fields = (
            "first_name",
            "last_name",
            "contact_phone",
            "location_zip",
            "location_city",
        )
