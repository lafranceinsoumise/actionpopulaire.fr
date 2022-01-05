import re

from django.contrib import admin
from django.contrib.postgres.search import SearchQuery
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.http import QueryDict, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse, path
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from agir.gestion.admin.base import BaseGestionModelAdmin
from agir.gestion.admin.depenses import DepenseListMixin
from agir.gestion.admin.filters import (
    DepenseResponsableFilter,
    ProjetResponsableFilter,
    InclureProjetsMilitantsFilter,
)
from agir.gestion.admin.forms import (
    DocumentForm,
    DepenseForm,
    ProjetForm,
    OrdreVirementForm,
)
from agir.gestion.admin.inlines import (
    VersionDocumentInline,
    ProjetParticipationInline,
    DepenseInline,
    AjouterDepenseInline,
    ProjetDocumentInline,
    DepenseDocumentInline,
    AjouterDocumentDepenseInline,
    AjouterDocumentProjetInline,
)
from agir.gestion.admin.views import AjouterReglementView
from agir.gestion.models import (
    Compte,
    Fournisseur,
    Document,
    Depense,
    Projet,
    InstanceCherchable,
)
from agir.gestion.models.depenses import etat_initial
from agir.gestion.models.projets import ProjetMilitant
from agir.gestion.models.virements import OrdreVirement
from agir.gestion.typologies import TypeDepense
from agir.gestion.utils import lien
from agir.lib.admin import display_list_of_links, AddRelatedLinkMixin
from agir.lib.display import display_price
from agir.lib.geo import FRENCH_COUNTRY_CODES
from agir.people.models import Person
from agir.gestion.permissions import peut_voir_montant_depense


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
class DocumentAdmin(BaseGestionModelAdmin, VersionAdmin):
    form = DocumentForm
    list_display = (
        "numero",
        "titre",
        "identifiant",
        "type",
        "requis",
    )

    inlines = (VersionDocumentInline,)

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
                )
            },
        ),
        ("Lié à", {"fields": ["depenses", "projets"]}),
        (
            "Ajouter une version de ce document",
            {"fields": ("titre_version", "fichier")},
        ),
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
class DepenseAdmin(DepenseListMixin, BaseGestionModelAdmin, VersionAdmin):
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
        "montant",
        "compte",
        "reglement",
    )

    readonly_fields = ("reglement", "reglements", "etat", "montant_interdit")

    autocomplete_fields = (
        "beneficiaires",
        "fournisseur",
        "depenses_refacturees",
    )
    inlines = [DepenseDocumentInline, AjouterDocumentDepenseInline]

    def get_fieldsets(self, request, obj=None):
        common_fields = [
            "numero_",
            "titre",
            "projet_link",
            "montant",
            "etat",
            "date_depense",
            "type",
            ("quantite", "nature"),
            "description",
        ]

        rel_fields = [
            "compte",
            "projet",
        ]

        paiement_fields = ["fournisseur", "reglements"]

        if obj and not peut_voir_montant_depense(request.user, obj):
            # on remplace le champ montant par un champ masqué
            common_fields[common_fields.index("montant")] = "montant_interdit"
            # on ne montre pas les règlements
            paiement_fields.remove("reglements")

        if request.GET.get("type") == TypeDepense.REFACTURATION or (
            obj is not None and obj.type == TypeDepense.REFACTURATION
        ):
            paiement_fields.remove("fournisseur")
            return (
                (None, {"fields": common_fields}),
                ("Gestion", {"fields": [*rel_fields, "depenses_refacturees"]}),
                ("Paiement", {"fields": paiement_fields}),
            )

        return (
            (None, {"fields": [*common_fields, "beneficiaires"]}),
            ("Gestion", {"fields": rel_fields}),
            ("Paiement", {"fields": paiement_fields}),
        )

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

        return render_to_string(
            "admin/gestion/table_reglements.html",
            {
                "depense": obj,
            },
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

        if "depenses_refacturees" in request.GET:
            try:
                initial["depenses_refacturees"] = Depense.objects.filter(
                    id__in=[
                        int(i) for i in request.GET["depenses_refacturees"].split(",")
                    ]
                )
            except ValueError:
                pass

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


class BaseProjetAdmin(BaseGestionModelAdmin, AddRelatedLinkMixin, VersionAdmin):
    date_hierarchy = "event__start_time"

    def event_name(self, obj):
        if obj and obj.event:
            return obj.event.name

    event_name.short_description = "Événement associé"
    event_name.admin_order_field = "event__name"

    def event_city(self, obj):
        if obj and obj.event:
            if obj.event.location_country in FRENCH_COUNTRY_CODES:
                return f"{obj.event.location_city} ({obj.event.location_zip})"
            return f"{obj.event.location_city}, {obj.event.location_country and obj.event.location_country.name}"

        return "-"

    event_city.short_description = "Lieu"
    event_city.admin_order_field = "event__location_zip"

    def event_location(self, obj):
        if obj and obj.event:
            e = obj.event
            lines = [
                e.location_address1,
                e.location_address2,
                f"{e.location_zip} {e.location_city}",
            ]

            if (
                e.location_country
                and e.location_country.code not in FRENCH_COUNTRY_CODES
            ):
                lines.append(e.location_country.name)

            return format_html_join(
                mark_safe("<br>"), "{}", ((l.strip(),) for l in lines if l.strip())
            )

        return "-"

    event_location.short_description = "Lieu"
    event_location.admin_order_field = "event__location_zip"

    def event_start_time(self, obj):
        if obj and obj.event:
            return obj.event.start_time
        return "-"

    event_start_time.short_description = "Quand"
    event_start_time.admin_order_field = "event__start_time"

    def event_schedule(self, obj):
        if obj and obj.event:
            return obj.event.get_display_date()
        return "-"

    event_schedule.short_description = "Quand"
    event_schedule.admin_order_field = "event__start_time"

    def event_organizer_persons(self, obj):
        if obj and obj.event:
            persons = obj.event.organizers.all()
            return display_list_of_links((p, str(p)) for p in persons)
        return "-"

    event_organizer_persons.short_description = "Organisateurs"

    def event_organizer_groups(self, obj):
        if obj and obj.event:
            groups = obj.event.organizers_groups.all()
            return display_list_of_links((g, str(g)) for g in groups)
        return "-"

    event_organizer_groups.short_description = "Groupes organisateurs"

    def event_contact(self, obj):
        if obj and (e := obj.event):
            lines = []
            if e.contact_name:
                lines.append(e.contact_name)
            if e.contact_email:
                lines.append(
                    format_html('<a href="{}">{}</a>', e.contact_email, e.contact_email)
                )
            if e.contact_phone:
                lines.append(e.contact_phone)

            return format_html_join(mark_safe("<br>"), "{}", ((l,) for l in lines))

        return "-"

    event_contact.short_description = "Informations de contact"

    def nb_depenses(self, obj):
        return getattr(obj, "nb_depenses", "-")

    nb_depenses.short_description = "Nombre de dépenses"
    nb_depenses.admin_order_field = "nb_depenses"

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + (
            "event_name",
            "event_city",
            "event_location",
            "event_start_time",
            "event_schedule",
            "event_organizer_persons",
            "event_organizer_groups",
            "event_contact",
            "nb_depenses",
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("event")
            .annotate(nb_depenses=Count("depense"))
        )


@admin.register(Projet)
class ProjetAdmin(BaseProjetAdmin):
    form = ProjetForm
    list_display = (
        "numero",
        "titre",
        "type",
        "etat",
        "event_name",
        "event_start_time",
        "event_city",
        "nb_depenses",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "numero_",
                    "titre",
                    "type",
                    "etat",
                    "origine",
                    "event",
                    "description",
                )
            },
        ),
        (
            "Détails de l'événement lié",
            {
                "fields": (
                    "event_link",
                    "event_location",
                    "event_schedule",
                    "event_organizer_persons",
                    "event_organizer_groups",
                    "event_contact",
                )
            },
        ),
    )

    readonly_fields = ("numero", "etat", "origine", "event_city", "event_start_time")
    autocomplete_fields = ("event",)

    inlines = [
        ProjetParticipationInline,
        DepenseInline,
        ProjetDocumentInline,
        AjouterDepenseInline,
        AjouterDocumentProjetInline,
    ]

    list_filter = (
        ProjetResponsableFilter,
        InclureProjetsMilitantsFilter,
        "type",
        "etat",
    )

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        if context["original"] is not None:
            qp = QueryDict(mutable=True)
            qp["type"] = TypeDepense.REFACTURATION
            qp["depenses_refacturees"] = ",".join(
                str(d.id) for d in context["original"].depenses.all()
            )
            context[
                "refacturation_url"
            ] = f'{reverse("admin:gestion_depense_add")}?{qp.urlencode()}'

        return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(ProjetMilitant)
class ProjetUtilisateurAdmin(BaseProjetAdmin):
    autocomplete_fields = ("event",)

    list_display = (
        "numero",
        "titre",
        "type",
        "etat",
        "event_name",
        "event_city",
        "event_start_time",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "numero_",
                    "titre",
                    "type",
                    "etat",
                    "event",
                    "description",
                )
            },
        ),
        (
            "Détails de l'événement lié",
            {
                "fields": (
                    "event_link",
                    "event_location",
                    "event_schedule",
                    "event_organizer_persons",
                    "event_organizer_groups",
                    "event_contact",
                )
            },
        ),
    )

    inlines = [
        ProjetDocumentInline,
    ]


@admin.register(OrdreVirement)
class OrdreVirementAdmin(BaseGestionModelAdmin, VersionAdmin):
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
    list_display = ("type_instance", "lien_instance")
    list_display_links = None

    search_fields = ("recherche",)

    def changelist_view(self, request, extra_context=None):
        q = request.GET.get("q", "").strip().upper()
        if self.NUMERO_RE.match(q):
            try:
                r = InstanceCherchable.objects.select_related("content_type").get(
                    numero=q
                )
            except InstanceCherchable.DoesNotExist:
                pass
            else:
                return HttpResponseRedirect(
                    reverse(
                        f"admin:{r.content_type.app_label}_{r.content_type.model}_change",
                        args=(r.object_id,),
                    )
                )

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

    def lien_numero(self, obj):
        return lien(obj.lien_admin(), obj.numero)

    lien_numero.short_description = "Numéro"

    def type_instance(self, obj):
        if obj is None:
            return "-"
        return obj.content_type.name

    type_instance.short_description = "Type d'objet"

    def lien_instance(self, obj):
        if obj is None:
            return "-"
        return lien(obj.lien_admin(), str(obj.instance))

    lien_instance.short_description = "Titre"
