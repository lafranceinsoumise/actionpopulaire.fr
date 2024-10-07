from typing import List, Optional

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import transaction
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from agir.events.models import Event
from agir.lib.admin.form_fields import SuggestingTextInput, CleavedDateInput
from ..admin.widgets import HierarchicalSelect
from ..models import (
    Commentaire,
    Depense,
    Fournisseur,
    Projet,
    Reglement,
    Compte,
)
from ..models.commentaires import ajouter_commentaire, nombre_commentaires_a_faire
from ..models.documents import Document, VersionDocument
from ..typologies import TypeDocument, TypeDepense, NATURE
from ..virements import generer_endtoend_id
from ...lib.form_mixins import ImportTableForm


class DocumentForm(forms.ModelForm):
    titre_version = forms.CharField(
        label="Nom de la version",
        required=False,
        help_text="Indiquez brièvement en quoi cette version diffère de la précédente.",
    )
    fichier = forms.FileField(label="Fichier de la version", required=False)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("titre_version") and not cleaned_data.get("fichier"):
            self.add_error(
                "fichier",
                ValidationError(
                    "Choisissez le fichier à télécharger pour cette nouvelle version.",
                    code="fichier_manquant",
                ),
            )
        elif cleaned_data.get("fichier") and not cleaned_data.get("titre_version"):
            self.add_error(
                "titre_version",
                ValidationError("Indiquez le titre de la nouvelle version du fichier"),
            )

    def _save_m2m(self):
        super()._save_m2m()

        if self.cleaned_data.get("fichier"):
            VersionDocument.objects.create(
                document=self.instance,
                titre=self.cleaned_data["titre_version"],
                fichier=self.cleaned_data["fichier"],
            )

    class Meta:
        model = Document
        fields = ()
        widgets = {"type": HierarchicalSelect}


class DocumentAjoutRapideForm(forms.ModelForm):
    """Formulaire pour ajouter rapidement un document à une dépense ou un projet.

    Du fait du fonctionnement de Django, ce ModelForm aura pour modèle le modèle de liaison entre la dépense ou le
    projet, et le document, et non le document lui même. C'est pour cette raison qu'on définit explicitement les champs.

    Petite particularité de Django : dans un inline, l'admin tente de récupérer label et help_text sur le modèle et pas
    sur le formulaire, ce qui est la raison pour laquelle ceux-ci sont définis ici dans la classe Meta (où Django va
    bien voir), et non directement sur les champs de formulaire.
    """

    type = forms.ChoiceField(
        choices=[("", "---")] + TypeDocument.choices,
        widget=HierarchicalSelect,
        required=True,
    )

    precision = forms.CharField(
        max_length=200,
        required=False,
    )

    identifiant = forms.CharField(
        max_length=100,
        required=False,
    )

    date = forms.DateField(required=False, widget=CleavedDateInput(today_button=False))

    fichier = forms.FileField(required=False)

    def save(self, commit=False):
        self.document = Document.objects.create(
            identifiant=self.cleaned_data.get("identifiant", ""),
            precision=self.cleaned_data.get("precision", ""),
            date=self.cleaned_data.get("date", ""),
            type=self.cleaned_data["type"],
        )

        self.instance.document = self.document

        return super().save(commit=commit)

    def _save_m2m(self):
        super()._save_m2m()
        if self.cleaned_data.get("fichier"):
            VersionDocument.objects.create(
                document=self.document,
                titre="Version initiale",
                fichier=self.cleaned_data["fichier"],
            )

    class Meta:
        # les labels et help_texts doivent être définis ici, voir doctext plus haut.
        labels = {
            f.name: f.verbose_name
            for f in Document._meta.get_fields()
            if getattr(f, "verbose_name", None) and f.verbose_name != f.name
        }

        help_texts = {
            f.name: f.help_text
            for f in Document._meta.get_fields()
            if getattr(f, "help_text", None)
        }


class DepenseForm(forms.ModelForm):
    type = forms.ChoiceField(
        label="Type de dépense",
        choices=TypeDepense.choices_avec_compte,
        widget=HierarchicalSelect(),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.type == TypeDepense.REFACTURATION and "montant" in self.fields:
            montant = self.get_initial_for_field(self.fields["montant"], "montant")
            total_factures = self.instance.depenses_refacturees.aggregate(
                Sum("montant")
            )["montant__sum"]

            if total_factures:
                if montant > total_factures:
                    self.fields["montant"].help_text = (
                        "Supérieur à la somme des dépenses à refacturer ({montant} €)x"
                    )
                else:
                    self.fields["montant"].help_text = (
                        f"Sur un total de {montant} € ({montant / total_factures:0.1%} %)."
                    )

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

    def clean_type(self):
        if TypeDepense(self.cleaned_data["type"]).compte is None:
            raise ValidationError(
                "Sélectionnez un type de dépense associé à un numéro de compte"
            )
        return self.cleaned_data["type"]

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
        widgets = {
            "nature": SuggestingTextInput(suggestions=NATURE),
            "date_depense": CleavedDateInput,
            "date_debut": CleavedDateInput,
            "date_fin": CleavedDateInput,
        }


class ProjetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance._state.adding:
            self.instance.etat = Projet.Etat.EN_CONSTITUTION

        if "event" in self.fields and (
            event := self.get_initial_for_field(self.fields["event"], "event")
        ):
            id = event.id if isinstance(event, Event) else event
            self.fields["event"].help_text = format_html(
                '<a href="{}">Accéder à la page de l\'événement</a>',
                reverse("admin:events_event_change", args=(id,)),
            )

    class Meta:
        model = Projet
        fields = ()
        widgets = {"type": HierarchicalSelect}


class CommentaireForm(forms.Form):
    type = forms.ChoiceField(
        label="Type",
        initial=Commentaire.Type.REM,
        choices=Commentaire.Type.choices,
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


class AjoutRapideDepenseForm(forms.ModelForm):
    type_document = forms.ChoiceField(
        label="Type de Document",
        choices=[("", "")] + TypeDocument.choices,
        widget=HierarchicalSelect,
        required=False,
    )
    fichier = forms.FileField(label="Fichier", required=False)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("type_document") and not cleaned_data.get("fichier"):
            self.add_error(
                "fichier",
                ValidationError(
                    "Sélectionnez le fichier correspondant au type de document choisi."
                ),
            )
        elif cleaned_data.get("fichier") and not cleaned_data.get("type_document"):
            self.add_error(
                "type_document",
                ValidationError("Indiquez de quel type de document il s'agit."),
            )

    def _save_m2m(self):
        super()._save_m2m()

        if self.cleaned_data.get("type_document") and self.cleaned_data.get("fichier"):
            type_document_label = TypeDocument(self.cleaned_data["type_document"]).label
            document = Document.objects.create(
                type=self.cleaned_data["type_document"],
                fichier=self.cleaned_data["fichier"],
            )
            self.instance.documents.add(document)

    class Meta:
        model = Depense
        fields = ()
        widgets = {"type": HierarchicalSelect}


class ReglementForm(forms.ModelForm):
    VIREMENT_PLATEFORME = "VP"

    CHAMPS_FOURNISSEURS = [
        "nom",
        "iban",
        "bic",
        "contact_phone",
        "contact_email",
        "location_address1",
        "location_address2",
        "location_city",
        "location_zip",
        "location_country",
    ]
    CHAMPS_FOURNISSEURS_REQUIS = ["nom", "location_city"]

    choix_mode = forms.ChoiceField(
        choices=(
            ("", "Choisissez un type de règlement"),
            ("Règlement à enregistrer", Reglement.Mode.choices),
            (
                "Via la plateforme",
                ((VIREMENT_PLATEFORME, "Virement à effectuer via la plateforme"),),
            ),
        ),
        required=True,
    )

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

        # on limite le choix de la facture à celles associées à la dépense
        facture_qs = depense.documents.filter(type=TypeDocument.FACTURE)
        self.fields["facture"].queryset = facture_qs
        # S'il n'y a qu'une seule facture associée à la dépense, on peut la présélectionner
        if len(facture_qs) == 1:
            self.fields["facture"].initial = facture_qs[0]

        # on pré-remplit les informations de Fournisseur s'il y en avait un de sélectionné.
        if depense.fournisseur:
            self.initial["fournisseur"] = depense.fournisseur

        self.fields["intitule"].initial = depense.identifiant_facture

        self.fields["nom_fournisseur"].required = False
        self.fields["location_city_fournisseur"].required = False
        self.fields["location_zip_fournisseur"].required = False

    def clean(self):
        # deux cas possibles pour le choix du fournisseur :
        # - soit on a choisi un fournisseur existant sans remplir aucun champ de fournisseur dans la section en-dessous
        # - soit on crée un nouveau fournisseur via la section inférieure
        super().clean()

        if any(
            f"{field}_fournisseur" in self.changed_data
            for field in self.CHAMPS_FOURNISSEURS
        ):
            # Il ne faut pas sélectionner de fournisseur dans ce cas
            if self.cleaned_data.get("fournisseur"):
                self.add_error(
                    "fournisseur",
                    ValidationError(
                        "Vous ne pouvez pas remplir les cases ci-dessous si vous avez sélectionné un fournisseur existant ici.",
                        code="nouveau_ou_existant",
                    ),
                )

            # cas de la création d'un nouveau fournisseur
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
                    f: self.cleaned_data[f"{f}_fournisseur"]
                    for f in self.CHAMPS_FOURNISSEURS
                    if f in self.cleaned_data
                }
            )

        else:
            # on utilise un fournisseur existant
            self.fournisseur = self.cleaned_data.get("fournisseur")
            if self.fournisseur:
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
            else:
                self.add_error(
                    "fournisseur",
                    ValidationError(
                        "Sélectionner un fournisseur ici, ou créez-en un nouveau grâce aux champs ci-dessous."
                    ),
                )

        if self.cleaned_data.get("choix_mode") == self.VIREMENT_PLATEFORME:
            # Si on enregistre un virement à effectuer via un ordre de virement
            # - il ne doit pas y avoir de preuve de paiement
            # - il faut avoir une désignation, l'IBAN et le BIC pour pouvoir effectuer un virement

            if self.cleaned_data.get("preuve"):
                self.add_error(
                    "preuve",
                    ValidationError(
                        "Il ne devrait pas y avoir de preuve de paiement pour un virement",
                        code="preuve_interdite",
                    ),
                )

            if not self.fournisseur.iban and "iban_fournisseur" not in self.errors:
                self.add_error(
                    (
                        "iban_fournisseur"
                        if self.fournisseur._state.adding
                        else "fournisseur"
                    ),
                    ValidationError(
                        "Un IBAN doit être indiqué pour le fournisseur pour réaliser un virement.",
                        code="iban_requis",
                    ),
                )

            # On n'indique que le BIC est requis si toutes les conditions suivantes s'appliquent
            # - l'utilisateur a fourni un IBAN
            # - l'utilisateur n'a pas fourni de BIC, et ce n'est pas suite à une erreur sur le champ BIC
            # - finalement, il n'est pas possible de générer un BIC à partir de l'IBAN
            if (
                self.fournisseur.iban
                and not self.fournisseur.bic
                and "bic_fournisseur" not in self.errors
            ):
                try:
                    self.fournisseur.iban.bic
                except AttributeError:
                    self.add_error(
                        (
                            "bic_fournisseur"
                            if self.fournisseur._state.adding
                            else "fournisseur"
                        ),
                        ValidationError(
                            "Le BIC doit être indiqué pour ce fournisseur (impossible de le déduire de l'IBAN).",
                            code="bic_requis",
                        ),
                    )

        # Pour les autres modes, il faut fournir la preuve que le paiement a été effectué
        elif self.cleaned_data.get("choix_mode"):
            if not self.cleaned_data.get("preuve") and "preuve" not in self.errors:
                self.add_error(
                    "preuve",
                    ValidationError(
                        "Vous devez fournir une preuve de paiement pour ce mode de règlement (le scan du chèque, le ticket de caisse, etc.)",
                        code="preuve_requise",
                    ),
                )

    def _save_m2m(self):
        """Gérer correctement la création de la preuve de paiement."""
        super()._save_m2m()

        reglement_modifie = False

        if self.cleaned_data.get("preuve"):
            self.preuve = Document.objects.create(
                type=TypeDocument.PAIEMENT,
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
        if self.cleaned_data["choix_mode"] == self.VIREMENT_PLATEFORME:
            self.instance.mode = Reglement.Mode.VIREMENT
        else:
            self.instance.mode = self.cleaned_data["choix_mode"]

        if not self.fournisseur._state.adding:
            # on copie les valeurs du fournisseur existant pour les conserver sur le règlement
            for f in self.CHAMPS_FOURNISSEURS:
                setattr(self.instance, f"{f}_fournisseur", getattr(self.fournisseur, f))

        if not self.cleaned_data.get("preuve"):
            self.instance.etat = Reglement.Etat.ATTENTE
        else:
            self.instance.etat = Reglement.Etat.REGLE

        return super().save(commit=commit)

    class Meta:
        model = Reglement
        fields = (
            "intitule",
            "numero",
            "montant",
            "facture",
            "date",
            "fournisseur",
            "nom_fournisseur",
            "iban_fournisseur",
            "bic_fournisseur",
            "contact_phone_fournisseur",
            "contact_email_fournisseur",
            "location_address1_fournisseur",
            "location_address2_fournisseur",
            "location_city_fournisseur",
            "location_zip_fournisseur",
            "location_country_fournisseur",
        )
        widgets = {"date": CleavedDateInput, "date_releve": CleavedDateInput}


class OrdreVirementForm(forms.ModelForm):
    reglements = forms.ModelMultipleChoiceField(
        queryset=Reglement.objects.filter(
            etat=Reglement.Etat.ATTENTE,
            mode=Reglement.Mode.VIREMENT,
            ordre_virement__isnull=True,
        ),
        required=True,
        widget=FilteredSelectMultiple(
            verbose_name="Règlements à inclure", is_stacked=False
        ),
    )

    def __init__(self, *args, compte=None, **kwargs):
        super().__init__(*args, **kwargs)

        if "reglements" in self._meta.fields:
            if compte is not None:
                self.fields["reglements"].queryset = self.fields[
                    "reglements"
                ].queryset.filter(depense__compte=compte)
        else:
            del self.fields["reglements"]

    def clean_reglements(self):
        value = self.cleaned_data["reglements"]
        id_comptes = {r.depense.compte for r in value}

        if len(id_comptes) > 1:
            raise ValidationError(
                "Impossible de créer un ordre de virement à partir de règlements provenant de plusieurs comptes.",
            )

        return value

    def _save_m2m(self):
        reglements = self.cleaned_data["reglements"].select_for_update()

        with transaction.atomic():
            for r in reglements:
                r.ordre_virement = self.instance
                if not r.endtoend_id:
                    r.endtoend_id = generer_endtoend_id()
                r.save(update_fields=["ordre_virement", "endtoend_id"])

        super()._save_m2m()


class InlineReglementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "facture" in self.fields:
            try:
                self.fields["facture"].queryset = (
                    self.instance.depense.documents.filter(type=TypeDocument.FACTURE)
                )
            except Depense.DoesNotExist:
                self.fields["facture"].queryset = Document.objects.none()


class ImportTableauVirementsForm(forms.Form):
    nom = forms.CharField(required=True, label="Nom")
    emetteur = forms.ModelChoiceField(
        queryset=Compte.objects.all(),
        required=True,
        label="Emetteur",
        help_text="Sélectionner le compte à partir duquel les virements vont être effectués",
    )
    tableau_virement_file = forms.FileField(
        required=True,
        help_text="""
        Fichier contant les virements pour la création de l'ordre.
        Sous format Excel, la première ligne contient les noms des colonnes,
        Les lignes suivantes correspondent aux virements.
        """,
        label="Tableau des virements",
    )


class TableauVirementsLierColonne(ImportTableForm):
    dest_columns = {
        "montant": "Montant",
        "description": "Motif",
        "iban": "IBAN",
        "nom": "Nom",
        "bic": "Bic",
    }

    def clean_columns(self, columns: List[Optional[str]]) -> List[Optional[str]]:
        columns = super().clean_columns(columns)
        required_columns = {"montant", "description", "iban", "nom"}
        if not required_columns.issubset(columns):
            raise forms.ValidationError(
                "Vous devez sélectionner toutes les colonnes, colonne(s) manquante(s): "
                + ",".join(required_columns.difference(columns))
            )
        return columns
