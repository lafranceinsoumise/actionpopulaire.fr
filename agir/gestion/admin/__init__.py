from django.contrib import admin
from django.utils.html import format_html, format_html_join
from reversion.admin import VersionAdmin

from agir.gestion.admin.base import BaseMixin
from agir.gestion.admin.forms import CommentairesForm, DocumentInlineForm
from agir.gestion.admin.inlines import (
    DepenseDocumentInline,
    DepenseInline,
    ProjetDocumentInline,
    ProjetParticipationInline,
)
from agir.gestion.models import (
    Depense,
    Projet,
    Compte,
    Document,
    Fournisseur,
)
from agir.lib.display import display_price


@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ("designation", "nom", "description")
    fields = ("designation", "nom", "description")


@admin.register(Fournisseur)
class FournisseurAdmin(VersionAdmin):
    list_display = ("nom", "contact_phone", "contact_email")

    fieldsets = (
        (None, {"fields": ("nom", "contact_phone", "contact_email")}),
        ("Paiement", {"fields": ("iban",)}),
        (
            "Adresse de facturation",
            {
                "fields": (
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "location_country",
                )
            },
        ),
    )

    search_fields = ("nom", "description")


@admin.register(Document)
class DocumentAdmin(BaseMixin, VersionAdmin):
    list_display = (
        "numero",
        "titre",
        "identifiant",
        "type",
        "requis",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "numero_",
                    "titre",
                    "identifiant",
                    "type",
                    "requis",
                    "fichier",
                )
            },
        ),
        (
            "Commentaires",
            {
                "fields": (
                    "bloc_commentaires",
                    "nouveau_commentaire",
                    "type_commentaire",
                )
            },
        ),
    )


@admin.register(Depense)
class DepenseAdmin(BaseMixin, VersionAdmin):
    list_filter = (
        "type",
        "compte",
    )

    list_display = (
        "numero_",
        "titre",
        "type",
        "montant",
        "date_depense",
        "compte",
        "projet",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "numero_",
                    "titre",
                    "compte",
                    "type",
                    "montant",
                    "description",
                    "date_depense",
                    "personnes",
                )
            },
        ),
        ("Informations de paiement", {"fields": ("fournisseur", "versements")}),
        (
            "Commentaires",
            {
                "fields": (
                    "bloc_commentaires",
                    "nouveau_commentaire",
                    "type_commentaire",
                )
            },
        ),
    )

    readonly_fields = ("versements",)

    def versements(self, obj):
        format_html(
            "<table><thead><tr><th>Date</th><th>Montant</th><th>Statut</th></thead></tr><tbody>{}</tbody>",
            format_html_join(
                "",
                "<tr><td>{date}</td><td>{montant}</td><td>{statut}</td>",
                (
                    {
                        "date": v.date.strftime("%d/%m/%Y"),
                        "montant": display_price(v.montant),
                        "statut": v.get_display_statut(),
                    }
                    for v in obj.versements.all()
                ),
            ),
        )

    versements.short_description = "Versements effectués"

    autocomplete_fields = (
        "personnes",
        "fournisseur",
    )
    inlines = [DepenseDocumentInline]


@admin.register(Projet)
class ProjetAdmin(BaseMixin, VersionAdmin):
    list_display = ("numero", "titre", "type", "statut")

    fieldsets = (
        (
            None,
            {"fields": ("numero_", "titre", "type", "statut", "event", "description")},
        ),
        (
            "Commentaires",
            {
                "fields": (
                    "bloc_commentaires",
                    "nouveau_commentaire",
                    "type_commentaire",
                )
            },
        ),
    )

    readonly_fields = ("numero",)
    autocomplete_fields = ("event",)

    inlines = [ProjetParticipationInline, DepenseInline, ProjetDocumentInline]
