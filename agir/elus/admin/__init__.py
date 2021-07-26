from datetime import datetime

import reversion
from reversion.admin import VersionAdmin
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
from psycopg2._range import DateRange

from agir.elus.models import (
    MandatMunicipal,
    MandatDepartemental,
    MandatRegional,
    RechercheParrainage,
    MandatConsulaire,
    AccesApplicationParrainages,
    MandatDepute,
    CHAMPS_ELUS_PARRAINAGES,
)
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
)
from .forms import (
    PERSON_FIELDS,
    MandatForm,
    MandatMunicipalForm,
    RechercheParrainageForm,
    MandatDepartementalForm,
    MandatDeputeForm,
)
from .views import ConfirmerParrainageView, AnnulerParrainageView
from ...lib.admin import display_list_of_links


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
                    for title, params in self.fieldsets
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
                    for _, params in self.fieldsets
                    for f in params["fields"]
                    if f in own_fields
                ]

                return (
                    ("Compte", {"fields": ("person", "create_new_person",),},),
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
                        for title, params in self.fieldsets
                    )
                )
                + additional_fieldsets
            )
        return self.fieldsets + additional_fieldsets

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
            "distance",
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

    def distance(self, obj):
        if obj.distance is None:
            return "-"

        if obj.distance == 0:
            return "Dans le périmètre"

        return f"{obj.distance.km:.0f} km"

    distance.short_description = "Distance entre l'adresse et le lieu d'élection"

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
            (m, m.titre_complet(conseil_avant=True),) for m in mandats if m != obj
        )

    mandats_municipaux.short_description = "Mandats municipaux"

    def mandats_departementaux(self, obj=None):
        person = obj.person

        mandats = MandatDepartemental.objects.filter(person=person)
        return display_list_of_links(
            (m, m.titre_complet(conseil_avant=True),) for m in mandats if m != obj
        )

    mandats_departementaux.short_description = "Mandats départementaux"

    def mandats_regionaux(self, obj=None):
        person = obj.person

        mandats = MandatRegional.objects.filter(person=person)
        return display_list_of_links(
            (m, m.titre_complet(conseil_avant=True),) for m in mandats if m != obj
        )

    mandats_regionaux.short_description = "Mandats régionaux"

    def membre_reseau_elus(self, object):
        return object.person.get_membre_reseau_elus_display()

    membre_reseau_elus.short_description = "Membre du réseau ?"
    membre_reseau_elus.admin_order_field = "person__membre_reseau_elus"


@admin.register(MandatMunicipal)
class MandatMunicipalAdmin(BaseMandatAdmin):
    form = MandatMunicipalForm
    autocomplete_fields = (
        "conseil",
        "reference",
    )

    list_filter = (
        "statut",
        "mandat",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
        ConseilFilter,
        DepartementFilter,
        DepartementRegionFilter,
        ReferenceFilter,
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
        ("Précisions sur le mandat", {"fields": ("dates", "delegations")},),
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

    class Media:
        pass


@admin.register(MandatDepartemental)
class MandatDepartementAdmin(BaseMandatAdmin):
    form = MandatDepartementalForm

    autocomplete_fields = ("conseil", "reference")
    list_filter = (
        "statut",
        "mandat",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
        ConseilFilter,
        RegionFilter,
        ReferenceFilter,
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
        ("Précisions sur le mandat", {"fields": ("dates", "delegations")},),
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
    list_filter = (
        "statut",
        "mandat",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
        RegionFilter,
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
        ("Précisions sur le mandat", {"fields": ("dates", "delegations")},),
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
    )

    readonly_fields = (
        "actif",
        "person_link",
    )

    def get_conseil_queryset(self, request):
        return CollectiviteRegionale.objects.all()

    class Media:
        pass


@admin.register(MandatConsulaire)
class MandatConsulaireAdmin(BaseMandatAdmin):
    list_filter = (
        "statut",
        "mandat",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
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
        ("Précisions sur le mandat", {"fields": ("dates",)},),
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
    )

    readonly_fields = (
        "actif",
        "person_link",
    )

    def get_conseil_queryset(self, request):
        return CirconscriptionConsulaire.objects.all()

    class Media:
        pass


@admin.register(MandatDepute)
class MandatDeputeAdmin(BaseMandatAdmin):
    form = MandatDeputeForm
    list_filter = (
        "statut",
        DatesFilter,
        "person__is_insoumise",
        "person__is_2022",
        AppelEluFilter,
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
        ("Précisions sur le mandat", {"fields": ("dates",)},),
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
    )

    readonly_fields = (
        "actif",
        "person_link",
    )
    autocomplete_fields = ("conseil",)

    def get_conseil_queryset(self, request):
        return CirconscriptionLegislative.objects.all()

    class Media:
        pass


@admin.register(RechercheParrainage)
class RechercherParrainageMaireAdmin(admin.ModelAdmin):
    form = RechercheParrainageForm

    autocomplete_fields = (*CHAMPS_ELUS_PARRAINAGES, "person")
    list_display = ("nom_elu", "type_elu_label", "person", "statut", "formulaire")
    readonly_fields = (
        "nom_elu",
        "type_elu_label",
        "statut_display",
        "person",
    )

    list_filter = ("statut", TypeEluFilter)
    fields = ("person", "statut_display", "commentaires", "formulaire")

    search_fields = ("elu_municipal__search",)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (
                    "Élu·e sollicité·e",
                    {
                        "fields": ("maire", "elu_departemental", "depute"),
                        "description": "Choisissez un élu à partir des sélecteurs suivants, en fonction de son type de mandat.",
                    },
                ),
                ("Détails", {"fields": ("commentaires", "formulaire")}),
            )

        return (
            ("Élu·e sollicité·e", {"fields": ("nom_elu", "type_elu_label")},),
            ("Détails", {"fields": self.get_fields(request, obj=obj)}),
        )

    def get_search_results(self, request, queryset, search_term):
        use_distinct = False
        if search_term:
            return (
                queryset.filter(
                    elu__search=SearchQuery(search_term, config="data_france_search")
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

            links = []

            if obj.statut != RechercheParrainage.Statut.VALIDEE and obj.formulaire:
                links.append(
                    (
                        reverse(
                            "admin:elus_rechercheparrainagemaire_confirmer",
                            args=(obj.id,),
                        ),
                        "Confirmer ce parrainage",
                    )
                )
            if obj.statut != RechercheParrainage.Statut.ANNULEE:
                links.append(
                    (
                        reverse(
                            "admin:elus_rechercheparrainagemaire_annuler",
                            args=(obj.id,),
                        ),
                        "Annuler ce parrainage",
                    )
                )

            return format_html(
                "<p>{statut}</p>{liens}",
                statut=statut,
                liens=format_html_join("", '<a class="button" href="{}">{}</a>', links),
            )

        return "-"

    def get_urls(self):
        urls = super().get_urls()

        return [
            path(
                "<path:object_id>/confirmer/",
                self.admin_site.admin_view(
                    ConfirmerParrainageView.as_view(model_admin=self),
                ),
                name="elus_rechercheparrainagemaire_confirmer",
            ),
            path(
                "<path:object_id>/annuler/",
                self.admin_site.admin_view(
                    AnnulerParrainageView.as_view(model_admin=self),
                ),
                name="elus_rechercheparrainagemaire_annuler",
            ),
        ] + urls


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


@admin.register(AccesApplicationParrainages)
class AccesApplicationParrainagesAdmin(VersionAdmin):
    list_display = ("person", "etat")
    list_filter = ("etat",)

    fields = ("person", "etat")
    autocomplete_fields = ("person",)


admin.site.unregister(Depute)


@admin.register(Depute)
class DeputeAdmin(OriginalDeputeAdmin):
    list_filter = OriginalDeputeAdmin.list_filter + (MandatsFilter,)
