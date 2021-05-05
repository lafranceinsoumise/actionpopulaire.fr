from django.contrib import admin

from agir.gestion.admin.base import BaseMixin
from agir.gestion.admin.forms import DocumentInlineForm, CommentaireFormset, DevisForm
from agir.gestion.models import Depense, Projet, Participation, Commentaire


class BaseDocumentInline(admin.TabularInline):
    extra = 0
    show_change_link = True
    form = DocumentInlineForm

    autocomplete_fields = ("document",)

    fields = ("document", *DocumentInlineForm.DOCUMENTS_FIELDS)


class DepenseDocumentInline(BaseDocumentInline):
    model = Depense.documents.through


class DepenseInline(BaseMixin, admin.TabularInline):
    verbose_name = "Dépense"
    verbose_name_plural = "Dépenses du projet"

    model = Depense
    extra = 0
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    fields = ("numero_", "titre", "type", "montant", "date_depense", "compte")
    readonly_fields = ("montant", "type", "date_depense", "compte")


class AjouterDepenseInline(admin.TabularInline):
    verbose_name_plural = "Ajout rapide de dépenses"
    model = Depense
    form = DevisForm
    extra = 1
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    fields = ("titre", "type", "montant", "compte", "devis")


class ProjetDocumentInline(BaseDocumentInline):
    model = Projet.documents.through


class ProjetParticipationInline(admin.TabularInline):
    verbose_name_plural = "Personnes impliquées dans ce projet"
    model = Participation
    extra = 1

    fields = ("person", "role", "precisions")
    autocomplete_fields = ("person",)
