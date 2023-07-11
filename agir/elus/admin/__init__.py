from datetime import datetime

import reversion
from data_france.admin import (
    EluMunicipalAdmin as OriginalEluMunicipalAdmin,
    DeputeAdmin as OriginalDeputeAdmin,
)
from data_france.models import (
    CirconscriptionConsulaire,
    CirconscriptionLegislative,
    Commune,
    CollectiviteDepartementale,
    CollectiviteRegionale,
    Depute,
    EluMunicipal,
)
from django.contrib import admin
from django.contrib.postgres.search import SearchQuery
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, path
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from psycopg2._range import DateRange
from reversion.admin import VersionAdmin

from agir.elus.models import (
    MandatMunicipal,
    MandatDepartemental,
    MandatRegional,
    RechercheParrainage,
    MandatConsulaire,
    AccesApplicationParrainages,
    MandatDepute,
    CHAMPS_ELUS_PARRAINAGES,
    MandatDeputeEuropeen,
    Candidature,
    Scrutin,
    Autorisation,
)
from agir.lib.admin.panels import AddRelatedLinkMixin
from agir.lib.admin.utils import get_admin_link, display_list_of_links
from agir.lib.search import PrefixSearchQuery
from agir.people.models import Person
from .filters import (
    ConseilFilter,
    DepartementFilter,
    DepartementRegionFilter,
    RegionFilter,
    DatesFilter,
    AppelEluFilter,
    ReferenceFilter,
    MandatsFilter,
    TypeEluFilter,
    ParrainagesFilter,
    ScrutinFilter,
)
from .forms import (
    PERSON_FIELDS,
    MandatForm,
    MandatMunicipalForm,
    RechercheParrainageForm,
    MandatDepartementalForm,
    MandatDeputeForm,
    MandatDeputeEuropeenForm,
    MandatRegionalForm,
)
from .views import (
    ExporterAccesApplication,
    ChangerStatutView,
)


class BaseMandatAdmin(admin.ModelAdmin):
    form = MandatForm
    add_form_template = "admin/change_form.html"
    change_form_template = "elus/admin/history_change_form.html"
    search_fields = ("person",)

    def get_conseil_queryset(self, request):
        raise NotImplementedError("Implémenter cette méthode est obligatoire")

    def get_form(self, request, obj=None, change=False, **kwargs):
        form_class = super(BaseMandatAdmin, self).get_form(
            request, obj, change, **kwargs
        )
        if "conseil" in form_class.base_fields:
            form_class.base_fields["conseil"].queryset = self.get_conseil_queryset(
                request
            )

        return form_class

    def get_fieldsets(self, request, obj=None):
        """Permet de ne pas afficher les mêmes champs à l'ajout et à la modification

        S'il y a ajout, on ne veux pas montrer le champ de choix de l'email officiel.
        S'il y a modification, on veut montrer le lien vers la personne plutôt que la personne.
        """
        can_view_person = request.user.has_perm("people.view_person")
        create_new_person = request.GET.get("nouvelle") == "O"
        original_fieldsets = super().get_fieldsets(request, obj=obj)

        # cas de la création d'un nouveau mandat
        if obj is None:
            # si on crée une nouvelle personne, on affiche tous les champs
            # sauf le choix d'une personne existante, et le choix d'un des
            # emails comme email officiel
            if create_new_person:
                return tuple(
                    (
                        title,
                        {
                            **params,
                            "fields": tuple(
                                f
                                for f in params["fields"]
                                if f not in ["email_officiel", "person"]
                            ),
                        },
                    )
                    for title, params in original_fieldsets
                )
            else:
                # Si on utilise une personne existante, on n'affiche que les champs
                # de sélection de la personne et des caractéristiques du mandat.
                # Afficher les champs de modification des caractéristiques de la personne
                # (nom, prénom, etc.) mènerait soit à ignorer les données saisies par
                # l'utilisateur, soit à écraser les données existantes sans les présenter
                # d'abord à l'utilisateur.
                own_fields = {f.name for f in self.model._meta.get_fields()}.difference(
                    ["person", "email_officiel"]
                )
                additional_fields = [
                    f
                    for _, params in original_fieldsets
                    for f in params["fields"]
                    if f in own_fields
                ]

                return (
                    (
                        "Compte",
                        {
                            "fields": (
                                "person",
                                "create_new_person",
                            ),
                        },
                    ),
                    ("Détails", {"fields": additional_fields}),
                )

        additional_fieldsets = ()
        if obj.person is not None:
            person = obj.person
            models = [MandatMunicipal, MandatDepartemental, MandatRegional]
            fields = [
                "mandats_municipaux",
                "mandats_departementaux",
                "mandats_regionaux",
            ]
            current_model = self.model
            querysets = [
                model.objects.exclude(id=obj.id)
                if model == current_model
                else model.objects.all()
                for model in models
            ]
            autres_mandats = [qs.filter(person=person).exists() for qs in querysets]

            if any(autres_mandats):
                additional_fieldsets += (
                    (
                        "Autres mandats",
                        {
                            "fields": tuple(
                                f for f, ex in zip(fields, autres_mandats) if ex
                            )
                        },
                    ),
                )

        if can_view_person:
            return (
                tuple(
                    (
                        (
                            title,
                            {
                                **params,
                                "fields": tuple(
                                    f if f != "person" else "person_link"
                                    for f in params["fields"]
                                ),
                            },
                        )
                        for title, params in original_fieldsets
                    )
                )
                + additional_fieldsets
            )
        return original_fieldsets + additional_fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj) + (
            "actif",
            "create_new_person",
            "person_link",
            "mandats_municipaux",
            "mandats_departementaux",
            "mandats_regionaux",
            "is_insoumise_display",
            "is_2022_display",
            "is_2022_appel_elus",
            "statut_parrainage",
            "parrainage_link",
        )

        if obj is not None:
            return readonly_fields + ("person",)
        return readonly_fields

    def get_autocomplete_fields(self, request):
        return super().get_autocomplete_fields(request) + ("person",)

    def get_search_results(self, request, queryset, search_term):
        use_distinct = False
        if search_term:
            return (
                queryset.filter(
                    person__search=PrefixSearchQuery(
                        search_term, config="simple_unaccented"
                    )
                ),
                use_distinct,
            )
        return queryset, use_distinct

    def create_new_person(self, obj):
        info = self.model._meta.app_label, self.model._meta.model_name
        return format_html(
            '<a href="{}">{}</a>',
            f'{reverse("admin:%s_%s_add" % info)}?nouvelle=O',
            "Créer un élu sans compte",
        )

    create_new_person.short_description = "Il s'agit d'un élu sans compte ?"

    def actif(self, obj):
        if obj:
            return obj.actif()
        return "-"

    actif.short_description = "Mandat en cours"
    actif.boolean = True

    def person_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:people_person_change", args=[obj.person_id]),
            str(obj.person),
        )

    person_link.short_description = "Profil de l'élu"

    def is_insoumise_display(self, obj):
        if obj.person:
            return obj.person.is_insoumise
        return None

    is_insoumise_display.short_description = "Insoumis⋅e"
    is_insoumise_display.boolean = True

    def is_2022_display(self, obj):
        if obj.person:
            return obj.person.is_2022
        return None

    is_2022_display.short_description = "Soutien 2022"
    is_2022_display.boolean = True

    def is_2022_appel_elus(self, obj):
        if obj.person:
            return (
                obj.person.meta.get("subscriptions", {}).get("NSP", {}).get("mandat")
                is not None
            )
        return None

    is_2022_appel_elus.short_description = "Soutien 2022 via appel élus"
    is_2022_appel_elus.boolean = True

    def get_changeform_initial_data(self, request):
        """Permet de préremplir le champs `dates' en fonction de la dernière élection"""
        initial = super().get_changeform_initial_data(request)

        if "person" in request.GET:
            try:
                initial["person"] = Person.objects.get(pk=request.GET["person"])
            except Person.DoesNotExist:
                pass

        if "conseil" in request.GET:
            try:
                initial["conseil"] = self.get_conseil_queryset(request).get(
                    code=request.GET["conseil"]
                )
            except ObjectDoesNotExist:
                pass

        if "debut" in request.GET and "fin" in request.GET:
            try:
                initial["dates"] = DateRange(
                    datetime.strptime(request.GET["debut"], "%Y-%m-%d").date(),
                    datetime.strptime(request.GET["fin"], "%Y-%m-%d").date(),
                )
            except ValueError:
                pass

        return initial

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        with reversion.create_revision():
            reversion.set_comment("Depuis l'interface d'aministration")
            reversion.set_user(request.user)
            return super().changeform_view(request, object_id, form_url, extra_context)

    def mandats_municipaux(self, obj=None):
        person = obj.person

        mandats = MandatMunicipal.objects.filter(person=person)

        return display_list_of_links(
            (
                m,
                m.titre_complet(conseil_avant=True),
            )
            for m in mandats
            if m != obj
        )

    mandats_municipaux.short_description = "Mandats municipaux"

    def mandats_departementaux(self, obj=None):
        person = obj.person

        mandats = MandatDepartemental.objects.filter(person=person)
        return display_list_of_links(
            (
                m,
                m.titre_complet(conseil_avant=True),
            )
            for m in mandats
            if m != obj
        )

    mandats_departementaux.short_description = "Mandats départementaux"

    def mandats_regionaux(self, obj=None):
        person = obj.person

        mandats = MandatRegional.objects.filter(person=person)
        return display_list_of_links(
            (
                m,
                m.titre_complet(conseil_avant=True),
            )
            for m in mandats
            if m != obj
        )

    mandats_regionaux.short_description = "Mandats régionaux"

    def membre_reseau_elus(self, object):
        return object.person.get_membre_reseau_elus_display()

    membre_reseau_elus.short_description = "Membre du réseau ?"
    membre_reseau_elus.admin_order_field = "person__membre_reseau_elus"

    def statut_parrainage(self, obj):
        if obj and obj.reference_id:
            try:
                parrainage = RechercheParrainage.trouver_parrainage(obj)
            except RechercheParrainage.DoesNotExist:
                pass
            else:
                return parrainage.get_statut_display()
        return "-"

    statut_parrainage.short_description = "Parrainage 2022"

    def parrainage_link(self, obj):
        if obj and obj.reference_id:
            try:
                parrainage = RechercheParrainage.trouver_parrainage(obj)
            except RechercheParrainage.DoesNotExist:
                pass
            else:
                return format_html(
                    '<a href="{}">{}</a>',
                    get_admin_link(parrainage),
                    parrainage.get_statut_display(),
                )
        return "-"


@admin.register(MandatMunicipal)
class MandatMunicipalAdmin(BaseMandatAdmin):
    form = MandatMunicipalForm
    autocomplete_fields = (
        "conseil",
        "reference",
    )
    readonly_fields = ("distance",)

    list_filter = (
        "statut",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
        "mandat",
        ConseilFilter,
        DepartementFilter,
        DepartementRegionFilter,
        ReferenceFilter,
        ParrainagesFilter,
    )

    list_display = (
        "person",
        "conseil",
        "mandat",
        "membre_reseau_elus",
        "statut",
        "actif",
        "communautaire",
        "is_insoumise_display",
        "is_2022_display",
        "is_2022_appel_elus",
        "statut_parrainage",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "person",
                    "conseil",
                    "statut",
                    "membre_reseau_elus",
                    "mandat",
                    "communautaire",
                    "is_insoumise",
                    "is_2022",
                    "signataire_appel",
                    "parrainage_link",
                    "reference",
                    "commentaires",
                )
            },
        ),
        (
            "Informations sur l'élu⋅e",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "email_officiel",
                    "contact_phone",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "distance",
                    "new_email",
                )
            },
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("dates", "delegations")},
        ),
    )

    def get_conseil_queryset(self, request):
        return Commune.objects.filter(
            type__in=[
                Commune.TYPE_COMMUNE,
                Commune.TYPE_SECTEUR_PLM,
                Commune.TYPE_COMMUNE_ASSOCIEE,
                Commune.TYPE_COMMUNE_DELEGUEE,
            ]
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("person")

    def distance(self, obj):
        if obj.distance is None:
            return "-"

        if obj.distance == 0:
            return "Dans le périmètre"

        return f"{obj.distance.km:.0f} km"

    distance.short_description = "Distance entre l'adresse et le lieu d'élection"

    class Media:
        pass


@admin.register(MandatDepartemental)
class MandatDepartementAdmin(BaseMandatAdmin):
    form = MandatDepartementalForm

    autocomplete_fields = ("conseil", "reference")
    list_filter = (
        "statut",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
        "mandat",
        ConseilFilter,
        RegionFilter,
        ReferenceFilter,
        ParrainagesFilter,
    )

    list_display = (
        "person",
        "conseil",
        "mandat",
        "membre_reseau_elus",
        "statut",
        "actif",
        "is_insoumise_display",
        "is_2022_display",
        "is_2022_appel_elus",
        "statut_parrainage",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "person",
                    "conseil",
                    "statut",
                    "membre_reseau_elus",
                    "mandat",
                    "is_insoumise",
                    "is_2022",
                    "signataire_appel",
                    "parrainage_link",
                    "reference",
                    "commentaires",
                )
            },
        ),
        (
            "Informations sur l'élu⋅e",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "email_officiel",
                    "contact_phone",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "new_email",
                )
            },
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("dates", "delegations")},
        ),
    )

    def get_conseil_queryset(self, request):
        # On n'autorise pas ces collectivités comme choix pour un élu départemental
        # Les élus de ces conseils doivent être ajoutés comme des élus régionaux.
        return CollectiviteDepartementale.objects.exclude(
            code__in=["20R", "75C", "972R", "973R", "976R"]
        )

    class Media:
        pass


@admin.register(MandatRegional)
class MandatRegionalAdmin(BaseMandatAdmin):
    form = MandatRegionalForm
    autocomplete_fields = ("reference",)
    list_filter = (
        "statut",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
        "mandat",
        RegionFilter,
        ReferenceFilter,
        ParrainagesFilter,
    )

    list_display = (
        "person",
        "conseil",
        "mandat",
        "membre_reseau_elus",
        "statut",
        "actif",
        "is_insoumise_display",
        "is_2022_display",
        "is_2022_appel_elus",
        "parrainage_link",
        "statut_parrainage",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "person",
                    "conseil",
                    "statut",
                    "membre_reseau_elus",
                    "mandat",
                    "is_insoumise",
                    "is_2022",
                    "signataire_appel",
                    "parrainage_link",
                    "reference",
                    "commentaires",
                )
            },
        ),
        (
            "Informations sur l'élu⋅e",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "email_officiel",
                    "contact_phone",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "new_email",
                )
            },
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("dates", "delegations")},
        ),
    )

    def get_conseil_queryset(self, request):
        return CollectiviteRegionale.objects.all()

    class Media:
        pass


@admin.register(MandatConsulaire)
class MandatConsulaireAdmin(BaseMandatAdmin):
    list_filter = ("mandat",)

    list_display = (
        "person",
        "conseil",
        "mandat",
        "membre_reseau_elus",
        "statut",
        "actif",
        "is_insoumise_display",
        "is_2022_display",
        "is_2022_appel_elus",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "person",
                    "conseil",
                    "statut",
                    "mandat",
                    "membre_reseau_elus",
                    "is_insoumise",
                    "is_2022",
                    "signataire_appel",
                    "commentaires",
                )
            },
        ),
        (
            "Informations sur l'élu⋅e",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "email_officiel",
                    "contact_phone",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "new_email",
                )
            },
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("dates",)},
        ),
    )

    def get_conseil_queryset(self, request):
        return CirconscriptionConsulaire.objects.all()

    class Media:
        pass


@admin.register(MandatDepute)
class MandatDeputeAdmin(BaseMandatAdmin):
    form = MandatDeputeForm

    autocomplete_fields = (
        "conseil",
        "reference",
    )
    list_filter = (
        "statut",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
        ReferenceFilter,
        ParrainagesFilter,
    )

    list_display = (
        "person",
        "conseil",
        "membre_reseau_elus",
        "statut",
        "actif",
        "is_insoumise_display",
        "is_2022_display",
        "is_2022_appel_elus",
        "statut_parrainage",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "person",
                    "conseil",
                    "statut",
                    "membre_reseau_elus",
                    "is_insoumise",
                    "is_2022",
                    "signataire_appel",
                    "parrainage_link",
                    "reference",
                    "commentaires",
                )
            },
        ),
        (
            "Informations sur l'élu⋅e",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "email_officiel",
                    "contact_phone",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "new_email",
                )
            },
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("dates",)},
        ),
    )

    def get_conseil_queryset(self, request):
        return CirconscriptionLegislative.objects.all()

    class Media:
        pass


@admin.register(MandatDeputeEuropeen)
class MandatDeputeEuropeenAdmin(BaseMandatAdmin):
    form = MandatDeputeEuropeenForm

    list_filter = (
        ReferenceFilter,
        ParrainagesFilter,
    )

    list_display = (
        "person",
        "membre_reseau_elus",
        "statut",
        "actif",
        "is_insoumise_display",
        "is_2022_display",
        "is_2022_appel_elus",
        "statut_parrainage",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "person",
                    "statut",
                    "membre_reseau_elus",
                    "is_insoumise",
                    "is_2022",
                    "signataire_appel",
                    "parrainage_link",
                    "reference",
                    "commentaires",
                )
            },
        ),
        (
            "Informations sur l'élu⋅e",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "email_officiel",
                    "contact_phone",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "new_email",
                )
            },
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("dates",)},
        ),
    )


@admin.register(RechercheParrainage)
class RechercheParrainageAdmin(admin.ModelAdmin):
    form = RechercheParrainageForm

    autocomplete_fields = (*CHAMPS_ELUS_PARRAINAGES, "person")
    list_display = (
        "nom_elu",
        "type_elu_label",
        "person",
        "statut",
        "formulaire",
        "parrainage",
    )
    readonly_fields = (
        "nom_elu",
        "type_elu_label",
        "statut_display",
        "person",
        "parrainage",
    )

    list_filter = ("statut", TypeEluFilter)
    fields = (
        "person",
        "statut_display",
        "commentaires",
        "commentaires_admin",
        "formulaire",
        "parrainage",
    )

    search_fields = ("search",)

    def get_fieldsets(self, request, obj=None):
        contact_fieldset = (
            "Contact",
            {"fields": ("email", "telephone", "adresse_postale")},
        )

        if obj is None:
            return (
                (
                    "Élu·e sollicité·e",
                    {
                        "fields": CHAMPS_ELUS_PARRAINAGES,
                        "description": "Choisissez un élu à partir des sélecteurs suivants, en fonction de son type de mandat.",
                    },
                ),
                ("Détails", {"fields": ("choix", "commentaires_admin", "formulaire")}),
                contact_fieldset,
            )

        return (
            (
                "Élu·e sollicité·e",
                {"fields": ("nom_elu", "type_elu_label")},
            ),
            ("Détails", {"fields": self.get_fields(request, obj=obj)}),
            contact_fieldset,
        )

    def get_search_results(self, request, queryset, search_term):
        use_distinct = False
        if search_term:
            return (
                queryset.filter(
                    search=SearchQuery(search_term, config="data_france_search")
                ),
                use_distinct,
            )
        return queryset, use_distinct

    def nom_elu(self, obj):
        if obj:
            if t := obj.type_elu:
                elu = getattr(obj, t)
                return f"{elu.nom}, {elu.prenom}"
            return "Élu·e supprimé·e"
        return "-"

    nom_elu.short_description = "Nom de l'élu·e"

    def type_elu_label(self, obj):
        if obj:
            if t := obj.type_elu:
                return self.model._meta.get_field(t).verbose_name
        return "-"

    type_elu_label.short_description = "Type de mandat"

    def statut_display(self, obj):
        if obj:
            statut = obj.get_statut_display()

            buttons = []

            if obj.statut == RechercheParrainage.Statut.VALIDEE:
                buttons.append(
                    (
                        RechercheParrainage.Statut.REVENU_SUR_ENGAGEMENT,
                        "Indiquer que l'élu·e est revenu·e sur son engagement",
                    )
                )
            if obj.statut != RechercheParrainage.Statut.VALIDEE and obj.formulaire:
                buttons.append(
                    (
                        RechercheParrainage.Statut.VALIDEE,
                        "Indiquer que l'engagement à parrainer est bien reçu",
                    )
                )
            if obj.statut != RechercheParrainage.Statut.ANNULEE:
                buttons.append(
                    (
                        RechercheParrainage.Statut.ANNULEE,
                        "Annuler ce parrainage",
                    )
                )

            return format_html(
                "<p>{statut}</p>{liens}",
                statut=statut,
                liens=format_html_join(
                    "",
                    '<button class="button" type="submit" form="statut_form" name="statut" value="{}">{}</button>',
                    buttons,
                ),
            )

        return "-"

    def get_urls(self):
        urls = super().get_urls()

        return [
            path(
                "<path:object_id>/statut/",
                self.admin_site.admin_view(
                    ChangerStatutView.as_view(model_admin=self),
                ),
                name="elus_rechercheparrainage_statut",
            ),
        ] + urls


@admin.register(AccesApplicationParrainages)
class AccesApplicationParrainagesAdmin(VersionAdmin):
    list_display = ("person", "etat")
    list_filter = ("etat",)

    fields = ("person", "etat")
    autocomplete_fields = ("person",)
    search_fields = ("people__search",)

    change_list_template = "elus/admin/accesapplicationparrainages/change_list.html"

    def get_search_results(self, request, queryset, search_term):
        usedistinct = False

        if search_term:
            return queryset.search(search_term), usedistinct

        return queryset, usedistinct

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name

        return [
            path(
                "export/",
                self.admin_site.admin_view(
                    ExporterAccesApplication.as_view(model_admin=self)
                ),
                name="%s_%s_export" % info,
            )
        ] + super().get_urls()


admin.site.unregister(EluMunicipal)


@admin.register(EluMunicipal)
class EluMunicipalAdmin(OriginalEluMunicipalAdmin):
    list_filter = OriginalEluMunicipalAdmin.list_filter + (MandatsFilter,)

    fieldsets = OriginalEluMunicipalAdmin.fieldsets + (
        ("Élus référencés", {"fields": ("mandats_associes",)}),
    )

    def mandats_associes(self, obj):
        if obj.id:
            ms = MandatMunicipal.objects.filter(reference=obj).select_related("person")

            return display_list_of_links((m, str(m.person)) for m in ms)

    mandats_associes.short_description = "Personnes associées à cette fiche"


admin.site.unregister(Depute)


@admin.register(Depute)
class DeputeAdmin(OriginalDeputeAdmin):
    list_filter = OriginalDeputeAdmin.list_filter + (MandatsFilter,)


@admin.register(Scrutin)
class ScrutinAdmin(admin.ModelAdmin):
    list_display = ("nom", "date", "type_scrutin", "circonscription_content_type")


@admin.register(Candidature)
class CandidatureAdmin(AddRelatedLinkMixin, admin.ModelAdmin):
    list_display = (
        "candidat",
        "sexe",
        "code_circonscription",
        "date",
        "etat",
        "ailleurs",
    )
    list_filter = (ScrutinFilter, "etat", "ailleurs", "sexe")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "code",
                    "person_link",
                    "scrutin_link",
                    "circonscription_link",
                )
            },
        ),
        ("État de la candidature", {"fields": ("date", "etat", "informations")}),
        (
            "État civil",
            {
                "fields": (
                    "nom",
                    "prenom",
                    "sexe",
                    "date_naissance",
                    "code_postal",
                    "ville",
                )
            },
        ),
        (
            "Informations supplémentaires",
            {
                "fields": (
                    "profession_foi",
                    "presence_en_ligne",
                    "reponses_questionnaire",
                    "meta",
                )
            },
        ),
    )

    readonly_fields = (
        "candidat",
        "code",
        "date",
        "nom",
        "prenom",
        "sexe",
        "date_naissance",
        "profession_foi",
        "meta",
        "code_circonscription",
        "circonscription_link",
        "reponses_questionnaire",
        "presence_en_ligne",
    )

    def get_queryset(self, request):
        """Rien de spécial implémenté ici, c'est dans le ScrutinView que se trouve la logique de filtrage"""
        return super().get_queryset(request)

    def candidat(self, obj):
        return f"{obj.nom} {obj.prenom}"

    candidat.short_description = "Candidat·e"
    candidat.admin_order_field = "nom"

    def reponses_questionnaire(self, obj):
        reponses = obj.meta.get("questionnaire", [])

        return format_html(
            "<dl>{}</dl>",
            format_html_join("", "<dt>{}</dt><dd>{}</dd>", reponses),
        )

    reponses_questionnaire.short_description = "Autres réponses au questionnaire"

    def code_circonscription(self, obj):
        return obj.code_circonscription

    code_circonscription.short_description = "Code circonscription"
    code_circonscription.admin_order_field = "code_circonscription"

    def circonscription_link(self, obj):
        circo = obj.circonscription

        return format_html('<a href="{}">{}</a>', get_admin_link(circo), str(circo))

    circonscription_link.short_description = "Circonscription de candidature"

    def presence_en_ligne(self, obj):
        liens = obj.meta.get("liens", [])
        return format_html_join(mark_safe("<br>"), '<a href="{}">{}</a>', liens)

    def has_module_permission(self, request):
        return super().has_module_permission(request) or (
            request.user.is_authenticated
            and Autorisation.objects.filter(groupe__user=request.user).exists()
        )

    def has_view_permission(self, request, obj=None):
        if obj is None:
            return (
                request.user.has_perm("elus.view_candidature")
                or Autorisation.objects.filter(groupe__user=request.user).exists()
            )

        return request.user.has_perm("elus.view_candidature") or request.user.has_perm(
            "elus.view_candidature", obj=obj
        )

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return request.user.has_perm("elus.change_candidature")

        return request.user.has_perm(
            "elus.change_candidature"
        ) or request.user.has_perm("elus.change_candidature", obj=obj)
