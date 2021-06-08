from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from agir.gestion.admin.widgets import HierarchicalSelect
from agir.gestion.models import (
    Commentaire,
    Depense,
    Document,
    Fournisseur,
    Projet,
    Reglement,
)
from agir.gestion.models.commentaires import ajouter_commentaire
from agir.gestion.typologies import TypeDocument, TypeDepense


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ()
        widgets = {"type": HierarchicalSelect}


class DepenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.type == TypeDepense.REFACTURATION and "montant" in self.fields:
            montant = self.get_initial_for_field(self.fields["montant"], "montant")
            total_factures = (
                self.instance.depenses_refacturees.aggregate(Sum("montant"))[
                    "montant__sum"
                ]
                or 0.0
            )

            if montant > total_factures:
                self.fields[
                    "montant"
                ].help_text = "Le montant de cette refacturation est pour le moment supérieur à la somme des dépenses à refacturer"
            else:
                pct = montant / total_factures * 100
                self.fields[
                    "montant"
                ].help_text = f"Cela représente {montant / total_factures:0.1%} % du total des dépenses refacturées."

        if "depenses_refacturees" in self.fields:
            depenses = self.get_initial_for_field(
                self.fields["depenses_refacturees"], "depenses_refacturees"
            )
            if depenses:
                self.fields["depenses_refacturees"].help_text = format_html(
                    "Accéder aux dépenses : {}",
                    format_html_join(
                        " — ",
                        '<a href="{}">{}</a>',
                        (
                            (
                                reverse("admin:gestion_depense_change", args=(d.id,)),
                                d.numero,
                            )
                            for d in depenses
                        ),
                    ),
                )

    def clean(self):
        cleaned_data = super().clean()

        errors = {}

        if cleaned_data.get("type") == TypeDepense.REFACTURATION and cleaned_data.get(
            "depenses_refacturees"
        ):
            if "compte" in cleaned_data and any(
                d.compte == cleaned_data["compte"]
                for d in cleaned_data["depenses_refacturees"]
            ):
                errors.setdefault("depenses_refacturees", []).append(
                    ValidationError(
                        "Vous ne pouvez refacturer que des dépenses d'un autre compte.",
                        code="refacturation_meme_compte",
                    )
                )

            if len({d.compte for d in cleaned_data["depenses_refacturees"]}) > 1:
                errors.setdefault("depenses_refacturees", []).append(
                    ValidationError(
                        "Toutes les dépenses refacturées doivent appartenir au même compte.",
                        code="refacturation_comptes_multiples",
                    )
                )

        if errors:
            raise ValidationError(errors)

        return cleaned_data

    class Meta:
        model = Depense
        fields = ()
        widgets = {"type": HierarchicalSelect}


class ProjetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance._state.adding:
            self.instance.etat = Projet.Etat.EN_CONSTITUTION

    class Meta:
        model = Projet
        fields = ()
        widgets = {"type": HierarchicalSelect}


class CommentaireForm(forms.Form):
    type = forms.ChoiceField(
        label="Type", initial=Commentaire.Type.REM, choices=Commentaire.Type.choices,
    )

    texte = forms.CharField(label="Texte", required=True, widget=forms.Textarea)

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, instance):
        ajouter_commentaire(
            instance,
            self.cleaned_data["texte"],
            self.cleaned_data["type"],
            self.user.person,
        )


class DepenseDevisForm(forms.ModelForm):
    devis = forms.FileField(label="Devis", max_length=30e6, required=False)  # 30 Mo

    def _save_m2m(self):
        if "devis" in self.cleaned_data:
            document = Document.objects.create(
                titre=f"Devis pour {self.instance.titre}",
                fichier=self.cleaned_data["devis"],
                type=TypeDocument.DEVIS,
            )
            self.instance.documents.add(document)

    class Meta:
        model = Depense
        fields = ()
        widgets = {"type": HierarchicalSelect}


class ReglementForm(forms.ModelForm):
    CHAMPS_FOURNISSEURS = [
        "nom",
        "iban",
        "contact_phone",
        "contact_email",
        "location_address1",
        "location_address2",
        "location_city",
        "location_zip",
        "location_country",
    ]
    CHAMPS_FOURNISSEURS_REQUIS = ["nom", "location_city"]

    preuve = forms.FileField(
        label="Preuve de paiement", help_text="Obligatoire, sauf pour les virements"
    )

    def __init__(self, *args, depense, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.depense = depense

        self.initial["intitule"] = depense.titre
        self.initial["montant"] = depense.montant

        # on pré-remplit les informations de Fournisseur s'il y en avait un de sélectionné.
        if depense.fournisseur:
            self.initial["fournisseur"] = depense.fournisseur

        self.fields["nom_fournisseur"].required = False
        self.fields["location_city_fournisseur"].required = False
        self.fields["location_zip_fournisseur"].required = False

        montant_max = depense.montant_restant
        self.fields["montant"].max_value = montant_max
        self.fields["montant"].validators.append(MaxValueValidator(montant_max))

    def clean(self):
        # Pour les virements, il faut nécessairement l'IBAN pour pouvoir effectuer le virement.

        if any(
            f"{field}_fournisseur" in self.changed_data
            for field in self.CHAMPS_FOURNISSEURS
        ):
            for f in self.CHAMPS_FOURNISSEURS_REQUIS:
                if not self.cleaned_data.get(f"{f}_fournisseur"):
                    print("prout")
                    self.add_error(
                        f"{f}_fournisseur",
                        ValidationError(
                            "Cette information est requise.", code=f"{f}_requis"
                        ),
                    )

            self.fournisseur = Fournisseur(
                **{
                    f: self.cleaned_data.get(f"{f}_fournisseur")
                    for f in self.CHAMPS_FOURNISSEURS
                }
            )

        else:
            self.fournisseur = self.cleaned_data.get("fournisseur")
            champs_fournisseurs_manquants = [
                f
                for f in self.CHAMPS_FOURNISSEURS_REQUIS
                if not getattr(self.fournisseur, f)
            ]
            if champs_fournisseurs_manquants:
                self.add_error(
                    "fournisseur",
                    "Les informations {} doivent être avoir été renseignées.".format(
                        " ,".join(
                            str(Fournisseur._meta.get_field(f).verbose_name)
                            for f in champs_fournisseurs_manquants
                        )
                    ),
                )

        if not self.fournisseur:
            self.add_error(
                "fournisseur",
                ValidationError(
                    "Sélectionner un fournisseur, ou créez-en un nouveau grâce aux champs ci-dessous."
                ),
            )

        if self.cleaned_data.get("mode") == Reglement.Mode.VIREMENT:
            if not self.fournisseur.iban and "iban_fournisseur" not in self.errors:
                self.add_error(
                    "iban_fournisseur"
                    if self.fournisseur._state.adding
                    else "fournisseur",
                    ValidationError(
                        "Un IBAN doit être indiqué pour le fournisseur pour réaliser un virement.",
                        code="iban_requis",
                    ),
                )

        # Pour les autres modes, il faut fournir la preuve que le paiement a été effectué
        elif self.cleaned_data.get("mode") in [
            Reglement.Mode.CASH,
            Reglement.Mode.CARTE,
            Reglement.Mode.CHEQUE,
        ]:
            if not self.cleaned_data.get("preuve") and "preuve" not in self.errors:
                self.add_error(
                    "preuve",
                    ValidationError(
                        "Vous devez fournir une preuve de paiement pour ce mode de réglement (le scan du chèque, le ticket de caisse, etc.)",
                        code="preuve_requise",
                    ),
                )

    def _save_m2m(self):
        """Gérer correctement la création de la preuve de paiement."""
        if self.cleaned_data.get("preuve"):
            self.preuve = Document.objects.create(
                titre=f"Preuve de paiement dépense {self.instance.depense.numero} — {self.instance.created.strftime('%d/%m/%Y')}",
                type=TypeDocument.PAIEMENT,
                requis=Document.Besoin.NECESSAIRE,
                description=f"Document créé automatiquement lors de l'ajout d'un règlement à la dépense "
                f"{self.depense.numero}.",
            )
            self.instance.preuve = self.preuve
            self.instance.save()

        if self.fournisseur._state.adding:
            self.fournisseur.save()

    def save(self, commit=True):
        if not self.cleaned_data.get("preuve"):
            self.instance.etat = Reglement.Statut.ATTENTE
        else:
            self.instance.etat = Reglement.Statut.REGLE

        return super().save(commit=commit)

    class Meta:
        model = Reglement
        fields = (
            "intitule",
            "mode",
            "montant",
            "date",
            "fournisseur",
            "nom_fournisseur",
            "iban_fournisseur",
            "contact_phone_fournisseur",
            "contact_email_fournisseur",
            "location_address1_fournisseur",
            "location_address2_fournisseur",
            "location_city_fournisseur",
            "location_zip_fournisseur",
            "location_country_fournisseur",
        )
