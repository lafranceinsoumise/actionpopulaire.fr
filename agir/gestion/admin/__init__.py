import re

from django.http import HttpResponseRedirect

from agir.gestion.models.common import ModeleGestionMixin
from django.contrib.postgres.search import SearchVector, SearchQuery

from agir.gestion.utils import lien
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from agir.gestion.admin.base import BaseAdminMixin
from agir.gestion.admin.filters import ProjetResponsableFilter, DepenseResponsableFilter
from agir.gestion.admin.forms import (
    DepenseForm,
    ProjetForm,
    DocumentForm,
    OrdreVirementForm,
)
from agir.gestion.admin.inlines import (
    DepenseDocumentInline,
    DepenseInline,
    ProjetDocumentInline,
    ProjetParticipationInline,
    AjouterDepenseInline,
)
from agir.gestion.admin.views import AjouterReglementView, TransitionView
from agir.gestion.models import (
    Depense,
    Projet,
    Fournisseur,
    Document,
    Compte,
    InstanceCherchable,
)
from agir.gestion.models.depenses import etat_initial
from agir.gestion.models.virements import OrdreVirement
from agir.gestion.typologies import TypeDepense
from agir.lib.display import display_price
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
            (None, {"fields": [*common_fields, "beneficiaires"]}),
            ("Gestion", {"fields": rel_fields}),
            ("Paiement", {"fields": ["fournisseur", "reglements"]}),
        )

    def montant_(self, obj):
        if obj:
            return display_price(obj.montant, price_in_cents=False)
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
        if obj is None:
            return "-"

        return render_to_string(
            "admin/gestion/table_reglements.html", {"depense": obj,}
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


@admin.register(OrdreVirement)
class OrdreVirementAdmin(BaseAdminMixin, VersionAdmin):
    form = OrdreVirementForm
    list_display = ("numero", "statut", "created", "date", "nb_reglements", "montant")

    fields = ("numero_", "statut", "created", "date", "reglements", "fichier")
    filter_horizontal = ("reglements",)

    readonly_fields = ("statut", "created", "fichier")

    def get_readonly_fields(self, request, obj=None):
        rof = super().get_readonly_fields(request, obj=obj)
        if obj:
            return [*rof, "reglements"]
        return rof

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                nb_reglements=Count("reglements"), montant=Sum("reglements__montant")
            )
        )

    def nb_reglements(self, obj):
        return getattr(obj, "nb_reglements", "-")

    nb_reglements.short_description = "Nombre de réglements"
    nb_reglements.admin_order_field = "nb_reglements"

    def montant(self, obj):
        total = getattr(obj, "montant")
        return display_price(total, price_in_cents=False) if total else "-"

    montant.short_description = "Montant total"
    montant.admin_order_field = "montant"


@admin.register(InstanceCherchable)
class InstanceCherchableAdmin(admin.ModelAdmin):
    NUMERO_RE = re.compile(r"^[A-Z0-9]{3}-[A-Z0-9]{3}$")
    list_display = ("content_type", "instance_link")
    list_display_links = None

    search_fields = ("recherche",)

    def changelist_view(self, request, extra_context=None):
        q = request.GET.get("q", "").strip().upper()
        if self.NUMERO_RE.match(q):
            for m in ModeleGestionMixin.__subclasses__():
                try:
                    return HttpResponseRedirect(
                        reverse(
                            f"admin:gestion_{m._meta.model_name}_change",
                            args=(
                                m.objects.values_list("id", flat=True).get(numero=q),
                            ),
                        )
                    )
                except m.DoesNotExist:
                    pass

        return super().changelist_view(request, extra_context=extra_context)

    def get_search_results(self, request, queryset, search_term):
        use_distinct = False
        if search_term:
            return (
                queryset.filter(
                    recherche=SearchQuery(search_term, config="french_unaccented")
                ),
                use_distinct,
            )

        return queryset, use_distinct

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def instance_link(self, obj):
        if obj is None:
            return "-"
        return lien(obj.lien_admin(), str(obj.instance))

    instance_link.short_description = "Page"
