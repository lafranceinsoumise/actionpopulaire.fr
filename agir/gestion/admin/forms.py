from django import forms

from agir.gestion.actions import ajouter_commentaire
from agir.gestion.models import Document
from agir.gestion.typologies import TypeCommentaire


class CommentairesForm(forms.ModelForm):
    nouveau_commentaire = forms.CharField(
        label="Ajouter un commentaire", required=False, widget=forms.Textarea()
    )
    type_commentaire = forms.ChoiceField(
        label="Type de commentaire", initial=TypeCommentaire.REM
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
    DOCUMENTS_FIELDS = ("titre", "type", "statut", "fichier")

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


class VersementForm(forms.ModelForm):
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

    preuve = forms.FileField(
        label="Preuve de paiement", help_text="Obligatoire, sauf pour les virements"
    )

    def __init__(self, *args, depense, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.depense = depense

        # on pré-remplit les informations de Fournisseur s'il y en avait un de sélectionné.
        if depense.fournisseur:
            self.initial["fournisseur"] = depense.fournisseur
            for f in self.CHAMPS_FOURNISSEURS:
                if getattr(depense.fournisseur, f):
                    self.initial[f] = getattr(depense.fournisseur, f)

    def clean(self):
        # Vérifier qu'on a les informations fournisseur dont on a besoin
        # Vérifier qu'on a les informations de preuve de paiement nécessaire en fonction du mode de paiement
        pass

    def _save_m2m(self):
        """Gérer correctement la création de la preuve de paiement."""
        pass

    def save(self, commit=True):
        # Quelle vérification ??
        return super().save(commit=commit)

    class Meta:
        fields = (
            "type",
            "montant",
            "date",
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
