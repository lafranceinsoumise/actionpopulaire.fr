from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html_join, format_html

from agir.gestion.admin.depenses import DepenseListMixin
from agir.gestion.admin.base import SearchableModelMixin
from agir.gestion.admin.forms import DepenseDevisForm
from agir.gestion.models import Depense, Projet, Participation
from agir.gestion.models.documents import VersionDocument


class BaseDocumentInline(admin.TabularInline):
    verbose_name = "Document associé"
    verbose_name_plural = "Documents associés"
    extra = 0
    show_change_link = True

    autocomplete_fields = ("document",)
    readonly_fields = ("type_document", "fichier_document")

    fields = ("document", "type_document", "fichier_document")

    def type_document(self, obj):
        if obj and obj.document:
            return obj.document.get_type_display()
        return "-"

    type_document.short_description = "Type de document"

    def fichier_document(self, obj):
        if obj and obj.document:
            doc = obj.document
            if doc.fichier:
                return format_html(
                    '<a href="{}">{}</a>', doc.fichier.url, doc.fichier.name
                )
            else:
                return "Pas encore de fichier"
        return "-"

    fichier_document.short_description = "Voir le fichier"


class DepenseDocumentInline(BaseDocumentInline):
    model = Depense.documents.through


class DepenseInline(DepenseListMixin, SearchableModelMixin, admin.TabularInline):
    verbose_name = "Dépense"
    verbose_name_plural = "Dépenses du projet"

    model = Depense
    extra = 0
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    fields = ("numero_", "titre", "type", "montant", "date_depense", "compte")
    readonly_fields = ("titre", "montant", "type", "date_depense", "compte")

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)
        if not request.user.has_perm("gestion.voir_montant_depense"):
            return tuple(f for f in fields if f != "montant")
        return fields


class AjouterDepenseInline(admin.TabularInline):
    verbose_name_plural = "Ajout rapide de dépenses"
    model = Depense
    form = DepenseDevisForm
    extra = 1
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    fields = ("titre", "type", "montant", "compte", "devis")


class ProjetDocumentInline(BaseDocumentInline):
    model = Projet.documents.through


def depense_type(type, label):
    def func(self, obj):
        if obj and obj.projet and obj.person:
            dep = obj.projet.depenses.filter(
                beneficiaires=obj.person, type__startswith=type
            )

            creation_url = "{}?projet={}&person={}&type={}".format(
                reverse("admin:gestion_depense_add"),
                obj.projet_id,
                obj.person_id,
                type,
            )
            add_button = format_html(
                '<div><a class="gestion--button" href="{}">Ajouter</a></div>',
                creation_url,
            )

            if dep:
                return format_html(
                    '<ul class="gestion--liste"><li>{}</li></ul>{}',
                    format_html_join(
                        "</li><li>",
                        '<a href="{}">{}</a>',
                        (
                            (
                                reverse("admin:gestion_depense_change", args=(d.id,)),
                                f"{d.numero} ({d.montant} €)",
                            )
                            for d in dep
                        ),
                    ),
                    add_button,
                )
            else:
                return add_button

        return "-"

    func.short_description = label
    return func


class ProjetParticipationInline(admin.TabularInline):
    verbose_name_plural = "Personnes impliquées dans ce projet"
    model = Participation
    extra = 1

    fields = (
        "person",
        "role",
        "precisions",
        "depense_transport",
        "depense_hebergement",
    )
    autocomplete_fields = ("person",)
    readonly_fields = ("depense_transport", "depense_hebergement")

    depense_transport = depense_type("TRA", "Dépenses de transport")
    depense_hebergement = depense_type("FRH", "Dépenses d'hébergement")


class VersionDocumentInline(admin.TabularInline):
    model = VersionDocument

    extra = 0
    show_change_link = True
    can_delete = True

    def has_add_permission(self, request, obj):
        return False

    fields = ("titre", "date", "fichier")
    readonly_fields = ("titre", "date", "fichier")
