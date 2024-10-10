import logging
import re
from functools import partial

import pandas as pd
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.postgres.search import SearchQuery
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction, router
from django.db.models import Count, Sum, Subquery, OuterRef, CharField, Value
from django.db.models.functions import Concat, LPad, Cast
from django.http import QueryDict, HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html_join, format_html
from django.utils.safestring import mark_safe
from django.views import View
from reversion.admin import VersionAdmin

from agir.events.models import Event
from agir.lib.admin.panels import AddRelatedLinkMixin
from agir.lib.admin.utils import display_list_of_links
from agir.lib.display import display_price
from agir.lib.geo import FRENCH_COUNTRY_CODES
from .base import BaseGestionModelAdmin
from .depenses import DepenseListMixin
from .filters import (
    DepenseResponsableFilter,
    ProjetResponsableFilter,
    InclureProjetsMilitantsFilter,
    FournisseurFilter,
)
from .forms import (
    DocumentForm,
    DepenseForm,
    ProjetForm,
    OrdreVirementForm,
    ImportTableauVirementsForm,
)
from .inlines import (
    VersionDocumentInline,
    ProjetParticipationInline,
    DepenseInline,
    AjouterDepenseInline,
    ProjetDocumentInline,
    DepenseDocumentInline,
    AjouterDocumentDepenseInline,
    AjouterDocumentProjetInline,
    DepenseReglementInline,
    OrdreVirementReglementInline,
    DepenseReglementLectureSeuleInline,
)
from .views import AjouterReglementView, ObtenirFichierOrdreVirementView
from ..models import (
    Compte,
    Fournisseur,
    Document,
    Depense,
    Projet,
    InstanceCherchable,
)
from ..models.depenses import etat_initial, Reglement
from ..models.ordre_virement import FichierOrdreDeVirement, Statut, Statut_couleur
from ..models.projets import ProjetMilitant
from ..models.virements import OrdreVirement
from ..permissions import peut_voir_montant_depense
from ..typologies import TypeDepense
from ..utils import lien

FICHIER_ORDRE_VIREMENT_NAMESPACE = "import_tableau_virement"
ORDRE_DE_VIREMENT_EMETTEUR_ID_NAMESPACE = "emetteur_id"
ORDRE_DE_VIREMENT_FILE_PATH_NAMESPACE = "file_path"


logger = logging.getLogger(__name__)


@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ("designation", "nom", "description")
    fieldsets = (
        (None, {"fields": ("designation", "nom", "description")}),
        (
            "Informations de l'émetteur",
            {"fields": ("emetteur_designation", "emetteur_iban", "emetteur_bic")},
        ),
        (
            "Informations de créditeur",
            {
                "fields": (
                    "beneficiaire_designation",
                    "beneficiaire_iban",
                    "beneficiaire_bic",
                )
            },
        ),
    )

    readonly_fields = ()

    def peut_emettre_virement(self, obj):
        return (
            obj.emetteur_designation
            and obj.emetteur_iban
            and obj.emetteur_iban.is_valid
            and obj.emetteur_bic
        )

    peut_emettre_virement.short_description = "Peut émettre des virements"
    peut_emettre_virement.boolean = True

    def peut_recevoir_virement(self, obj):
        return (
            obj.beneficiaire_designation
            and obj.beneficiaire_iban
            and obj.beneficiaire_iban.is_valid
            and obj.beneficiaire_bic
        )

    peut_recevoir_virement.short_description = "Peut recevoir des virements"
    peut_recevoir_virement.boolean = True


@admin.register(Fournisseur)
class FournisseurAdmin(VersionAdmin):
    list_display = ("nom", "contact_phone", "contact_email")

    CHAMPS_PERSONNES_MORALES = ["siren"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "type",
                    "nom",
                    "contact_phone",
                    "contact_email",
                    "siren",
                    "depenses",
                )
            },
        ),
        (
            "Paiement",
            {
                "fields": (
                    "iban",
                    "bic",
                )
            },
        ),
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

    readonly_fields = ("depenses",)
    search_fields = ("nom", "description")

    def depenses(self, obj):
        if obj is not None:
            return format_html(
                '<a href="{}">voir toutes les dépenses<a>',
                f'{reverse("admin:gestion_depense_changelist")}?fournisseur={obj.id}',
            )
        return "-"

    depenses.short_description = "dépenses"


@admin.register(Document)
class DocumentAdmin(BaseGestionModelAdmin, VersionAdmin):
    form = DocumentForm
    list_display = (
        "numero",
        "identifiant",
        "type",
        "date",
        "precision",
    )

    inlines = (VersionDocumentInline,)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "numero_",
                    "numero_piece",
                    "type",
                    "date",
                    "identifiant",
                    "precision",
                    "source_url",
                )
            },
        ),
        (
            "Lié à",
            {
                "fields": [
                    "comme_preuve_paiement",
                    "comme_facture",
                    "depenses",
                    "projets",
                ]
            },
        ),
        (
            "Ajouter une version de ce document",
            {"fields": ("titre_version", "fichier")},
        ),
    )
    readonly_fields = (
        "comme_preuve_paiement",
        "comme_facture",
        "depenses",
        "projets",
        "numero_piece",
    )

    def comme_facture(self, obj):
        if obj is not None:
            rs = obj.comme_facture.all()
            if rs:
                return format_html_join(
                    mark_safe("<br>"),
                    '<a href="{}">{}</a>',
                    (
                        (
                            reverse(
                                "admin:gestion_reglement_change",
                                args=(r.id,),
                            ),
                            f"{r.intitule}",
                        )
                        for r in rs
                    ),
                )
        return "-"

    def comme_preuve_paiement(self, obj):
        if obj is not None:
            rs = obj.comme_preuve_paiement.all()
            if rs:
                return format_html_join(
                    mark_safe("<br>"),
                    '<a href="{}">{}</a>',
                    (
                        (
                            reverse(
                                "admin:gestion_reglement_change",
                                args=(r.id,),
                            ),
                            f"{r.intitule}",
                        )
                        for r in rs
                    ),
                )
        return "-"

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
                mark_safe("<br>"),
                '<a href="{}">{}</a>',
                (
                    (
                        reverse("admin:gestion_projet_change", args=(p.id,)),
                        f"{p.numero} — {p.titre}",
                    )
                    for p in ps
                ),
            )

        return "-"


@admin.register(Depense)
class DepenseAdmin(DepenseListMixin, BaseGestionModelAdmin, VersionAdmin):
    NATURE_DESCRIPTION = """
    Ces champs doivent être remplies pour les dépenses d'impression et d'achat de matériel. 
    """

    form = DepenseForm

    list_filter = (
        DepenseResponsableFilter,
        "compte",
        "etat",
        FournisseurFilter,
        "type",
    )

    list_display = (
        "numero_",
        "date_evenement",
        "date_depense",
        "titre",
        "type",
        "etat",
        "montant",
        "compte",
        "reglement",
    )

    readonly_fields = (
        "reglement",
        "reglements",
        "etat",
        "montant_interdit",
        "date_evenement",
    )

    autocomplete_fields = (
        "projet",
        "fournisseur",
        "depenses_refacturees",
    )
    inlines = [
        DepenseReglementLectureSeuleInline,
        DepenseReglementInline,
        DepenseDocumentInline,
        AjouterDocumentDepenseInline,
    ]

    def get_fieldsets(self, request, obj=None):
        common_fields = [
            "numero_",
            "titre",
            "projet_link",
            "montant",
            "etat",
            "date_depense",
            "type",
            "description",
        ]

        nature_fields = ["quantite", "nature", "date_debut", "date_fin"]

        rel_fields = ["compte", "projet", "date_evenement"]

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
            (None, {"fields": common_fields}),
            ("Gestion", {"fields": rel_fields}),
            (
                "Nature de la dépense",
                {"fields": nature_fields, "description": self.NATURE_DESCRIPTION},
            ),
            ("Paiement", {"fields": paiement_fields}),
        )

    def date_evenement(self, obj):
        d = getattr(obj, "_date_evenement", None)

        if d:
            return d.strftime("%d/%m/%Y")

        return "-"

    date_evenement.short_description = "Date de l'événement"
    date_evenement.admin_order_field = "_date_evenement"

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

        return format_html(
            '{}<br><a href="{}">Ajouter un règlement</a>',
            self.reglement(obj),
            reverse("admin:gestion_depense_reglement", args=(obj.id,)),
        )

    reglements.short_description = "État du règlement"

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if not change:
            obj.etat = etat_initial(obj, request.user)
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annoter_reglement().annotate(
            _date_evenement=Subquery(
                Event.objects.filter(projet__depense=OuterRef("id")).values(
                    "start_time"
                )[:1]
            )
        )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

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

    def has_change_permission(self, request, obj=None):
        autorise = super().has_change_permission(request, obj=obj)
        if obj is None:
            return autorise and request.user.has_perm("gestion.valider_depense")

        if obj.etat == Depense.Etat.FEC:
            return False

        if obj.etat == Depense.Etat.EXPERTISE:
            return autorise and (
                request.user.has_perm("gestion.validation_depense")
                or request.user.has_perm("gestion.validation_depense", obj=obj.compte)
            )

        return autorise

    class Media:
        # media empty pour l'autocomplete filter
        pass


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
        "origine",
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
                    "date_evenement",
                    "code_insee",
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
            context["refacturation_url"] = (
                f'{reverse("admin:gestion_depense_add")}?{qp.urlencode()}'
            )

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
    change_list_template = "admin/gestion/ordrevirement/change_list.html"
    form = OrdreVirementForm
    list_display = ("numero", "statut", "created", "date", "nb_reglements", "montant")

    fields = (
        "numero_",
        "statut",
        "created",
        "date",
        "obtenir_fichier",
    )

    readonly_fields = ("statut", "created", "date", "obtenir_fichier")

    inlines = ()

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        if obj is not None:
            inlines = tuple([OrdreVirementReglementInline, *inlines])
        return inlines

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)
        if not obj:
            return ("reglements",)
        return fields

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                nb_reglements=Count("reglement"), montant=Sum("reglement__montant")
            )
        )

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context.setdefault(
            "comptes", Compte.objects.filter(actif=True).order_by("designation")
        )

        return super(OrdreVirementAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    def add_view(self, request, form_url="", extra_context=None):
        if not request.GET.get("compte"):
            return HttpResponseRedirect(
                reverse("admin:gestion_ordrevirement_changelist")
            )

        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form_klass = super().get_form(request, obj=None, change=False, **kwargs)

        if request.GET.get("compte"):
            try:
                form_klass = partial(
                    form_klass,
                    compte=Compte.objects.get(designation=request.GET["compte"]),
                )
            except Compte.DoesNotExist:
                pass

        return form_klass

    def get_urls(self):
        return [
            path(
                "fichier/<int:object_id>",
                self.admin_site.admin_view(ObtenirFichierOrdreVirementView.as_view()),
                name=f"gestion_ordrevirement_fichier",
            ),
            *super().get_urls(),
        ]

    def nb_reglements(self, obj):
        return getattr(obj, "nb_reglements", "-")

    nb_reglements.short_description = "Nombre de règlements"
    nb_reglements.admin_order_field = "nb_reglements"

    def montant(self, obj):
        total = getattr(obj, "montant")
        return display_price(total, price_in_cents=False) if total else "-"

    montant.short_description = "Montant total"
    montant.admin_order_field = "montant"

    def obtenir_fichier(self, obj):
        if obj.pk:
            return format_html(
                '<a class="button" href="{}">Obtenir le fichier</a>',
                reverse("admin:gestion_ordrevirement_fichier", args=(obj.pk,)),
            )


@admin.register(InstanceCherchable)
class InstanceCherchableAdmin(admin.ModelAdmin):
    NUMERO_RE = re.compile(r"^[A-Z0-9]{3}-[A-Z0-9]{3}$")
    NUMERO_PIECE_RE = re.compile(r"^\d{12}$")
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
        elif self.NUMERO_PIECE_RE.match(q):
            try:
                d = Document.objects.get(numero_piece=q)
            except Document.DoesNotExist:
                pass
            else:
                return HttpResponseRedirect(
                    reverse(f"admin:gestion_document_change", args=(d.object_id,))
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


@admin.register(Reglement)
class ReglementAdmin(BaseGestionModelAdmin):
    list_display = (
        "numero_complet",
        "intitule",
        "date",
        "montant",
        "etat",
        "mode",
        "compte_link",
        "depense_link",
    )

    list_filter = ("etat", "mode", "depense__compte")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "numero",
                    "intitule",
                    "etat",
                    "date",
                    "date_releve",
                    "montant",
                    "mode",
                )
            },
        ),
        (
            "Infos complémentaires pour le FECC",
            {
                "fields": (
                    "numero_compte",
                    "code_insee",
                    "date_evenement",
                    "libre",
                )
            },
        ),
        (
            "Liens avec d'autres entités",
            {
                "fields": (
                    "depense_link",
                    "compte_link",
                    "fournisseur_link",
                    "preuve_link",
                    "facture_link",
                )
            },
        ),
        (
            "Pour les paiements via la plateforme",
            {
                "fields": (
                    "endtoend_id",
                    "ordre_virement_link",
                )
            },
        ),
    )

    readonly_fields = ("numero_complet", "etat", "endtoend_id", "compte_link")

    def has_change_permission(self, request, obj=None):
        autorise = super().has_change_permission(request, obj=obj)
        if obj is None:
            return autorise and request.user.has_perm("gestion.valider_depense")

        if obj.etat == Reglement.Etat.FEC:
            return False

        if obj.etat == Reglement.Etat.EXPERTISE:
            return autorise and (
                request.user.has_perm("gestion.valider_depense")
                or request.user.has_perm(
                    "gestion.valider_depense", obj=obj.depense.compte
                )
            )

        return autorise

    def has_add_permission(self, request):
        return False

    @admin.display(description="Compte")
    def compte_link(self, obj):
        try:
            return lien(
                reverse("admin:gestion_compte_change", args=(obj.depense.compte_id,)),
                obj.depense.compte.designation,
            )
        except (Depense.DoesNotExist, Compte.DoesNotExist):
            return "-"

    @admin.display(
        description="Numéro dans le FECC",
        ordering=Concat(
            LPad(Cast("numero", output_field=CharField()), 5, Value("0")),
            "numero_complement",
        ),
    )
    def numero_complet(self, obj):
        return obj.numero_complet


@admin.register(FichierOrdreDeVirement)
class FichierOrdreVirementAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "compte_emetteur",
        "created",
        "statut_colored",
        "montant_total_currency",
        "iban_copy",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "nom",
                    "id",
                    "created",
                    "statut",
                    "compte_emetteur",
                    "iban_copy",
                    "nombre_transaction",
                    "montant_total_currency",
                    "tableau_virement_file",
                    "tableau_virement_gsheet",
                    "ordre_de_virement_out",
                )
            },
        ),
    )
    readonly_fields = (
        "id",
        "created",
        "compte_emetteur",
        "iban_copy",
        "bic_copy",
        "nombre_transaction",
        "montant_total_currency",
        "ordre_de_virement_out",
    )

    actions = ["mark_transmis_banque", "mark_virement_valide", "mark_cree"]

    @admin.action(description="Transmis à la banque")
    def mark_transmis_banque(self, request, queryset):
        queryset.update(statut=Statut.TRANSMIS)

    @admin.action(description="Virement validé")
    def mark_virement_valide(self, request, queryset):
        queryset.update(statut=Statut.VALIDE)

    @admin.action(description="Passer en état créé")
    def mark_cree(self, request, queryset):
        queryset.update(statut=Statut.CREE)

    @admin.display(description="Statut")
    def statut_colored(self, obj):
        return format_html(
            '<span style="padding: 3px;background-color: {};">{}</span>',
            Statut_couleur[obj.statut],
            Statut(obj.statut).label.upper(),
        )

    @admin.display(description="Montant total")
    def montant_total_currency(self, obj):
        return display_price(obj.montant_total)

    def add_view(self, request, form_url="", extra_context=None):
        with transaction.atomic(using=router.db_for_write(FichierOrdreDeVirement)):
            if not self.has_add_permission(request):
                raise PermissionDenied
            if request.method == "POST":
                form = ImportTableauVirementsForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()

                    return HttpResponseRedirect(
                        reverse("admin:gestion_fichierordredevirement_changelist")
                    )
            else:
                form = ImportTableauVirementsForm()
            fieldsets = ((None, {"fields": list(form.fields.keys())}),)
            admin_form = helpers.AdminForm(form, fieldsets, {}, model_admin=self)

            context = {
                **self.admin_site.each_context(request),
                "title": "Importation fichier de virements",
                "subtitle": None,
                "adminform": admin_form,
                "object_id": None,
                "original": None,
                "is_popup": False,
                "to_field": None,
                "media": None,
                "inline_admin_formsets": (),
                "errors": helpers.AdminErrorList(form, ()),
                "preserved_filters": self.get_preserved_filters(request),
            }
            context.update(extra_context or {})

            return self.render_change_form(
                request, context, add=True, change=False, form_url=form_url
            )
