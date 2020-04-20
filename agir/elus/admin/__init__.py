from datetime import datetime

import reversion
from data_france.models import Commune
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from agir.api.admin import admin_site
from agir.elus.admin.filters import (
    CommuneFilter,
    DepartementFilter,
    RegionFilter,
    CommunautaireFilter,
)
from agir.elus.admin.forms import PERSON_FIELDS, CreerMandatForm
from agir.elus.models import MandatMunicipal
from agir.lib.search import PrefixSearchQuery
from agir.people.models import Person


@admin.register(MandatMunicipal, site=admin_site)
class MandatMunicipalAdmin(admin.ModelAdmin):
    form = CreerMandatForm
    add_form_template = "admin/change_form.html"
    change_form_template = "elus/admin/change_form.html"

    list_filter = (
        "reseau",
        "mandat",
        CommunautaireFilter,
        CommuneFilter,
        DepartementFilter,
        RegionFilter,
    )

    fieldsets = (
        (None, {"fields": ("person", "commune", "mandat", "communautaire")}),
        (
            "Informations sur l'élu⋅e",
            {"fields": (*PERSON_FIELDS, "email_officiel", "new_email", "reseau",)},
        ),
        (
            "Précisions sur le mandat",
            {"fields": ("debut", "fin", "delegations_municipales")},
        ),
    )

    list_display = (
        "person",
        "commune",
        "mandat",
        "reseau",
        "actif",
        "communautaire",
        "is_insoumise",
    )

    readonly_fields = (
        "actif",
        "person_link",
    )
    autocomplete_fields = ("person", "commune")

    search_fields = ("person",)

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

    def actif(self, obj):
        return "Oui" if (obj.debut <= timezone.now().date() <= obj.fin) else "Non"

    actif.short_description = "Mandat en cours"

    def person_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:people_person_change", args=[obj.person_id]),
            str(obj.person),
        )

    person_link.short_description = "Profil de l'élu"

    def is_insoumise(self, obj):
        if obj.person:
            return "Oui" if obj.person.is_insoumise else "Non"
        return "-"

    is_insoumise.short_description = "Insoumis⋅e"

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + ("person", "commune")
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        """Permet de ne pas afficher les mêmes champs à l'ajout et à la modification

        S'il y a ajout, on ne veux pas montrer le champ de choix de l'email officiel.

        S'il y a modification, on veut montrer le lien vers la personne plutôt que la personne.
        """
        can_view_person = request.user.has_perm("people.view_person")

        if obj is None:
            return tuple(
                (
                    title,
                    {
                        **params,
                        "fields": tuple(
                            f for f in params["fields"] if f != "email_officiel"
                        ),
                    },
                )
                for title, params in self.fieldsets
            )

        elif can_view_person:
            return tuple(
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
        return self.fieldsets

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)

        if "person" in request.GET:
            try:
                initial["person"] = Person.objects.get(pk=request.GET["person"])
            except Person.DoesNotExist:
                pass

        if "commune" in request.GET:
            try:
                initial["commune"] = Commune.objects.get(code=request.GET["commune"])
            except Commune.DoesNotExist:
                pass

        if "debut" in request.GET:
            try:
                initial["debut"] = datetime.strptime(request.GET["debut"], "%Y-%m-%d")
            except ValueError:
                pass

        if "fin" in request.GET:
            try:
                initial["fin"] = datetime.strptime(request.GET["fin"], "%Y-%m-%d")
            except ValueError:
                pass

        return initial

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        with reversion.create_revision():
            reversion.set_comment("Depuis l'interface d'aministration")
            reversion.set_user(request.user)
            return super().changeform_view(request, object_id, form_url, extra_context)

    class Media:
        pass
