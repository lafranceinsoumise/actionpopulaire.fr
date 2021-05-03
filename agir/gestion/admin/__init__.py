from functools import partial

from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from agir.gestion.admin.base import BaseAdminMixin
from agir.gestion.admin.forms import DocumentInlineForm
from agir.gestion.admin.inlines import (
    DepenseDocumentInline,
    DepenseInline,
    ProjetDocumentInline,
    ProjetParticipationInline,
    AjouterDepenseInline,
)
from agir.gestion.admin.views import AjouterReglementView
from agir.gestion.models import (
    Depense,
    Projet,
    Compte,
    Document,
    Fournisseur,
)


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
class DocumentAdmin(BaseAdminMixin, VersionAdmin):
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
    )


@admin.register(Depense)
class DepenseAdmin(BaseAdminMixin, VersionAdmin):
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
                    "montant",
                    "type",
                    "compte",
                    "description",
                    "date_depense",
                    "personnes",
                )
            },
        ),
        ("Informations de paiement", {"fields": ("fournisseur", "reglements")}),
    )

    readonly_fields = ("reglements",)

    autocomplete_fields = (
        "personnes",
        "fournisseur",
    )
    inlines = [DepenseDocumentInline]

    def reglements(self, obj):
        if obj.reglements.exists():
            table = format_html(
                "<table><thead><tr><th>Date</th><th>Montant</th><th>Statut</th></thead></tr><tbody>{}</tbody>",
                format_html_join(
                    "",
                    "<tr><td>{date}</td><td>{montant}</td><td>{statut}</td>",
                    (
                        {
                            "date": v.date.strftime("%d/%m/%Y"),
                            "montant": "{}\u00A0€".format(v.montant),
                            "statut": v.get_display_statut(),
                        }
                        for v in obj.reglements.all()
                    ),
                ),
            )
        else:
            table = mark_safe("<div>Aucun réglement effectué pour le moment.</div>")

        return format_html(
            '{table}<div><a href="{link}">Ajouter un réglement</a>',
            table=table,
            link=reverse("admin:gestion_depense_reglement", args=(obj.id,)),
        )

    reglements.short_description = "règlements effectués"

    def get_urls(self):
        urls = super(DepenseAdmin, self).get_urls()
        additional_urls = [
            path(
                "<int:pk>/reglement/",
                self.admin_site.admin_view(
                    AjouterReglementView.as_view(model_admin=self)
                ),
                name="gestion_depense_reglement",
            )
        ]

        return additional_urls + urls


@admin.register(Projet)
class ProjetAdmin(BaseAdminMixin, VersionAdmin):
    list_display = ("numero", "titre", "type", "statut")

    fieldsets = (
        (
            None,
            {"fields": ("numero_", "titre", "type", "statut", "event", "description")},
        ),
    )

    readonly_fields = ("numero",)
    autocomplete_fields = ("event",)

    inlines = [
        ProjetParticipationInline,
        DepenseInline,
        AjouterDepenseInline,
        ProjetDocumentInline,
    ]

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        for inline in context["inline_admin_formsets"]:
            print(inline.opts, inline.formset.errors)
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj
        )
