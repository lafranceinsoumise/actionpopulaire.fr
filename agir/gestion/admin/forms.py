from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
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
        super()._save_m2m()

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
        label="Preuve de paiement",
        help_text="Obligatoire, sauf pour les virements",
        required=False,
    )

    def __init__(self, *args, depense, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.depense = depense
        montant_restant = depense.montant_restant

        self.initial["intitule"] = depense.titre
        self.initial["montant"] = montant_restant

        # on pré-remplit les informations de Fournisseur s'il y en avait un de sélectionné.
        if depense.fournisseur:
            self.initial["fournisseur"] = depense.fournisseur

        self.fields["nom_fournisseur"].required = False
        self.fields["location_city_fournisseur"].required = False
        self.fields["location_zip_fournisseur"].required = False

        self.fields["montant"].max_value = montant_restant
        self.fields["montant"].validators.append(MaxValueValidator(montant_restant))

    def clean_montant(self):
        if self.cleaned_data["montant"] <= 0:
            raise ValidationError(
                "Le montant réglé doit être strictement positif.",
                code="amount_not_positive",
            )
        return self.cleaned_data["montant"]

    def clean(self):
        # Pour les virements, il faut nécessairement l'IBAN pour pouvoir effectuer le virement.

        if any(
            f"{field}_fournisseur" in self.changed_data
            for field in self.CHAMPS_FOURNISSEURS
        ):
            for f in self.CHAMPS_FOURNISSEURS_REQUIS:
                if not self.cleaned_data.get(f"{f}_fournisseur"):
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

        if (
            self.cleaned_data.get("mode") == Reglement.Mode.VIREMENT
            and "preuve" not in self.cleaned_data
        ):
            # Si on enregistre un virement à effectuer via un ordre de virement (en l'absence de preuve)
            # il faut bien sûr avoir l'IBAN du fournisseur
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
        super()._save_m2m()

        reglement_modifie = False

        if "preuve" in self.cleaned_data:
            self.preuve = Document.objects.create(
                titre=f"Preuve réglement {self.instance.intitule} — dépense {self.instance.depense.numero}",
                type=TypeDocument.PAIEMENT,
                requis=Document.Besoin.NECESSAIRE,
                fichier=self.cleaned_data["preuve"],
                description=f"Document créé automatiquement lors de l'ajout d'un règlement à la dépense "
                f"{self.instance.depense.numero}.",
            )
            self.instance.preuve = self.preuve
            reglement_modifie = True

        if self.fournisseur._state.adding:
            self.fournisseur.save()
            self.instance.fournisseur = self.fournisseur
            reglement_modifie = True
            if not self.instance.depense.fournisseur:
                self.instance.depense.fournisseur = self.fournisseur
                self.instance.depense.save()

        if reglement_modifie:
            self.instance.save()

    def save(self, commit=True):
        if "preuve" not in self.cleaned_data:
            self.instance.statut = Reglement.Statut.ATTENTE
        else:
            self.instance.statut = Reglement.Statut.REGLE

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


class OrdreVirementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "reglements" in self.fields:
            self.fields["reglements"].queryset = self.fields[
                "reglements"
            ].queryset.filter(
                statut=Reglement.Statut.ATTENTE, mode=Reglement.Mode.VIREMENT
            )

        if "date" in self.fields:
            today = timezone.now().astimezone(timezone.get_current_timezone()).date()
            self.fields["date"].min_value = today
            self.fields["date"].validators.append(
                validators.MinValueValidator(
                    today,
                    message="Impossible de créer un ordre de virement dans le passé",
                )
            )

    def _save_m2m(self):
        # TODO: créer l'ordre de virement avec sepaxml et le sauvegarder
        super()._save_m2m()
