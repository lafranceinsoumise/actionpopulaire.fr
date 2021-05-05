from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

from agir.gestion.actions.commentaires import ajouter_commentaire
from agir.gestion.admin.widgets import HierarchicalSelect
from agir.gestion.models import (
    Document,
    Reglement,
    Fournisseur,
    Commentaire,
    Depense,
    Projet,
)
from agir.gestion.typologies import TypeDocument


class CommentairesForm(forms.ModelForm):
    nouveau_commentaire = forms.CharField(
        label="Ajouter un commentaire", required=False, widget=forms.Textarea()
    )
    type_commentaire = forms.ChoiceField(
        label="Type de commentaire",
        initial=Commentaire.Type.REM,
        choices=Commentaire.Type.choices,
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if self.cleaned_data.get("nouveau_commentaire"):
            ajouter_commentaire(
                self.instance,
                self.cleaned_data["nouveau_commentaire"],
                self.cleaned_data["type_commentaire"],
                self.user.person,
            )
        return super().save(commit=commit)


class DocumentInlineForm(forms.ModelForm):
    DOCUMENTS_FIELDS = ("titre", "type", "fichier")

    def __init__(self, *args, initial=None, instance=None, **kwargs):
        if initial is None:
            initial = {}

        if instance and instance.document:
            for f in self.DOCUMENTS_FIELDS:
                initial.setdefault(f, getattr(instance.document, f))

        super().__init__(*args, instance=instance, initial=initial, **kwargs)

        if instance and instance.document:
            self.fields["document"].disabled = True
        else:
            for f in self.DOCUMENTS_FIELDS:
                self.fields[f].disabled = True


_document_fields = {
    f.name: f.formfield()
    for f in Document._meta.get_fields()
    if f.name in DocumentInlineForm.DOCUMENTS_FIELDS
}
_document_fields.update(DocumentInlineForm.declared_fields)
DocumentInlineForm.base_fields = DocumentInlineForm.declared_fields = _document_fields


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


class BaseCommentaireFormset(forms.BaseModelFormSet):
    def __init__(
        self,
        data=None,
        files=None,
        instance=None,
        save_as_new=False,
        prefix=None,
        queryset=None,
        **kwargs,
    ):
        self.instance = instance

        if save_as_new:
            raise ValueError("Impossible d'utiliser save_as_new")

        if queryset is None:
            queryset = Commentaire.objects.all()

        qs = queryset.intersection(self.instance.commentaires.all())

        super().__init__(data, files, prefix=prefix, queryset=qs, **kwargs)


class DocumentForm(CommentairesForm, forms.ModelForm):
    class Meta:
        model = Document
        fields = ()
        widgets = {"type": HierarchicalSelect}


class DepenseForm(CommentairesForm, forms.ModelForm):
    class Meta:
        model = Depense
        fields = ()
        widgets = {"type": HierarchicalSelect}


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


class ProjetForm(CommentairesForm, forms.ModelForm):
    class Meta:
        model = Projet
        fields = ()
        widgets = {"type": HierarchicalSelect}
