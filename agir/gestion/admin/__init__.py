from agir.gestion.models.depenses import etat_initial

from agir.gestion.typologies import TypeDepense
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from agir.gestion.admin.base import BaseAdminMixin
from agir.gestion.admin.filters import ProjetResponsableFilter, DepenseResponsableFilter
from agir.gestion.admin.forms import (
    DepenseForm,
    ProjetForm,
    DocumentForm,
)
from agir.gestion.admin.inlines import (
    DepenseDocumentInline,
    DepenseInline,
    ProjetDocumentInline,
    ProjetParticipationInline,
    AjouterDepenseInline,
)
from agir.gestion.admin.views import AjouterReglementView, TransitionView
from agir.gestion.models import Depense, Projet, Fournisseur, Document, Compte
from agir.gestion.utils import montrer_montant
from agir.people.models import Person


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
    form = DocumentForm
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
        ("Lié à", {"fields": ["depenses", "projets"]}),
    )
    readonly_fields = ("depenses", "projets")

    def depenses(self, obj):
        if obj is not None:
            ds = obj.depenses.all()
            if ds:
                try:
                    return format_html_join(
                        mark_safe("<br>"),
                        '<a href="{}">{}</a>',
                        (
                            (
                                reverse("admin:gestion_depense_change", args=(d.id,)),
                                f"{d.numero} — {d.titre} — {d.montant} €",
                            )
                            for d in ds
                        ),
                    )
                except Exception as e:
                    print(e)
        return "-"

    depenses.short_description = "dépenses"

    def projets(self, obj):
        ps = obj.projets.all()
        if ps:
            return format_html_join(
                "<br>",
                '<a href="{}">{}</a>',
                (
                    (
                        reverse("admin:gestion_projet_change", args=(p.id,)),
                        f"{p.numero} — {p.nom}",
                    )
                    for p in ps
                ),
            )

        return "-"


@admin.register(Depense)
class DepenseAdmin(BaseAdminMixin, VersionAdmin):
    form = DepenseForm

    list_filter = (
        DepenseResponsableFilter,
        "compte",
        "type",
    )

    list_display = (
        "numero_",
        "date_depense",
        "titre",
        "type",
        "etat",
        "montant_",
        "compte",
        "reglement",
    )

    readonly_fields = ("montant_", "reglement", "reglements", "etat")

    autocomplete_fields = (
        "projet",
        "beneficiaires",
        "fournisseur",
        "depenses_refacturees",
    )
    inlines = [DepenseDocumentInline]

    def get_fieldsets(self, request, obj=None):
        common_fields = [
            "numero_",
            "titre",
            "montant",
            "etat",
            "date_depense",
            "type",
            "description",
        ]

        rel_fields = [
            "compte",
            "projet",
        ]

        if obj is not None and obj.type == TypeDepense.REFACTURATION:
            return (
                (None, {"fields": common_fields}),
                ("Gestion", {"fields": [*rel_fields, "depenses_refacturees"]}),
                ("Paiement", {"fields": ["reglements"]}),
            )

        return (
            (None, {"fields": common_fields}),
            ("Gestion", {"fields": rel_fields}),
            ("Paiement", {"fields": ["fournisseur", "reglements"]}),
        )

    def montant_(self, obj):
        if obj:
            return montrer_montant(obj.montant)
        return "-"

    montant_.short_description = "Montant"
    montant_.admin_order_field = "montant"

    def reglement(self, obj):
        if obj is None or obj.prevu is None:
            return "Non réglée"

        if obj.prevu < obj.montant:
            return "Partiellement prévue"

        if obj.regle is None:
            return "Prévu mais non réglée"

        if obj.regle < obj.montant:
            return "Partiellement réglée"

        return "Réglée"

    def reglements(self, obj):
        if obj is None or obj.id is None:
            return "-"

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

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if not change:
            obj.etat = etat_initial(obj, request.user)
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).annoter_reglement()

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        if "person" in request.GET:
            try:
                initial["beneficiaires"] = [
                    Person.objects.get(id=request.GET["person"])
                ]
            except (Person.DoesNotExist, ValidationError):
                pass

        if "projet" in request.GET:
            try:
                initial["projet"] = Projet.objects.get(id=request.GET["projet"])
            except (Projet.DoesNotExist, ValueError):
                initial["projet"] = None

        if "type" in request.GET:
            initial["type"] = request.GET["type"]

        return initial

    def get_urls(self):
        urls = super().get_urls()
        additional_urls = [
            path(
                "<int:object_id>/reglement/",
                self.admin_site.admin_view(
                    AjouterReglementView.as_view(model_admin=self)
                ),
                name="gestion_depense_reglement",
            ),
        ]

        return additional_urls + urls


@admin.register(Projet)
class ProjetAdmin(BaseAdminMixin, VersionAdmin):
    form = ProjetForm
    list_display = ("numero", "titre", "type", "etat", "event")

    fieldsets = (
        (
            None,
            {"fields": ("numero_", "titre", "type", "etat", "event", "description")},
        ),
    )

    readonly_fields = ("numero", "etat")
    autocomplete_fields = ("event",)

    inlines = [
        ProjetParticipationInline,
        DepenseInline,
        AjouterDepenseInline,
        ProjetDocumentInline,
    ]

    list_filter = (
        ProjetResponsableFilter,
        "type",
        "etat",
    )
