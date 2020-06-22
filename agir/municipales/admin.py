from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.measure import D
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, path
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from functools import reduce, update_wrapper
from operator import or_

from agir.municipales.models import CommunePage, Liste
from agir.people.models import Person


class CheffeDeFileFilter(SimpleListFilter):
    title = "Chef⋅fes de fil"
    parameter_name = "cheffes_file"

    def lookups(self, request, model_admin):
        return (
            ("O", "Uniquement les communes avec"),
            ("N", "Uniquement les communes sans"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "O":
            return queryset.exclude(chefs_file=None)
        elif value == "N":
            return queryset.filter(chefs_file=None)
        return queryset


class CommuneForm(forms.ModelForm):
    liste_soutenue_tour_1 = forms.ModelChoiceField(
        label="Liste soutenue par la FI — 1er tour",
        queryset=Liste.objects.none(),
        empty_label="Aucune",
        required=False,
    )
    type_soutien_tour_1 = forms.ChoiceField(
        label="Type de soutien — 1er tour",
        choices=[
            (Liste.SOUTIEN_PUBLIC, "Soutien public"),
            (Liste.SOUTIEN_PREF, "Simple préférence"),
        ],
        initial="P",
        required="P",
    )

    liste_soutenue_tour_2 = forms.ModelChoiceField(
        label="Liste soutenue par la FI — 2ème tour",
        queryset=Liste.objects.none(),
        empty_label="Aucune",
        required=False,
    )
    type_soutien_tour_2 = forms.ChoiceField(
        label="Type de soutien — 2ème tour",
        choices=[
            (Liste.SOUTIEN_PUBLIC, "Soutien public"),
            (Liste.SOUTIEN_PREF, "Simple préférence"),
        ],
        initial="P",
        required="P",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        listes_tour_1 = self.instance.listes.filter(tour=1)
        listes_tour_2 = self.instance.listes.filter(tour=2)

        self.fields["liste_soutenue_tour_1"].queryset = listes_tour_1
        self.fields["liste_soutenue_tour_2"].queryset = listes_tour_2

        try:
            self.liste_soutenue_tour_1 = listes_tour_1.exclude(
                soutien=Liste.SOUTIEN_NON
            ).get()
            self.fields["liste_soutenue_tour_1"].initial = self.liste_soutenue_tour_1
            self.fields[
                "type_soutien_tour_1"
            ].initial = self.liste_soutenue_tour_1.soutien
        except Liste.DoesNotExist:
            self.liste_soutenue_tour_1 = None

        try:
            self.liste_soutenue_tour_2 = listes_tour_2.exclude(
                soutien=Liste.SOUTIEN_NON
            ).get()
            self.fields["liste_soutenue_tour_2"].initial = self.liste_soutenue_tour_2
            self.fields[
                "type_soutien_tour_2"
            ].initial = self.liste_soutenue_tour_2.soutien
        except Liste.DoesNotExist:
            self.liste_soutenue_tour_2 = None

    def _save_m2m(self):
        super()._save_m2m()

        nouvelle_liste_soutenue = self.cleaned_data["liste_soutenue"]

        if "liste_soutenue" in self.changed_data or "type_soutien" in self.changed_data:
            with transaction.atomic():
                if (
                    self.liste_soutenue is not None
                    and self.liste_soutenue != nouvelle_liste_soutenue
                ):
                    self.liste_soutenue.soutien = Liste.SOUTIEN_NON
                    self.liste_soutenue.save(update_fields=["soutien"])

                if nouvelle_liste_soutenue is not None:
                    nouvelle_liste_soutenue.soutien = self.cleaned_data["type_soutien"]
                    nouvelle_liste_soutenue.save(update_fields=["soutien"])


@admin.register(CommunePage)
class CommunePageAdmin(admin.ModelAdmin):
    form = CommuneForm
    readonly_fields = (
        "code",
        "code_departement",
        "name",
        "municipales2020_people_list",
    )
    fieldsets = (
        (None, {"fields": ("code", "code_departement", "name")}),
        (
            "Campagne FI",
            {
                "fields": (
                    "published",
                    "contact_email",
                    "mandataire_email",
                    "first_name_1",
                    "last_name_1",
                    "first_name_2",
                    "last_name_2",
                )
            },
        ),
        (
            "Premier tour",
            {
                "fields": (
                    "liste_tour_1",
                    "liste_soutenue_tour_1",
                    "type_soutien_tour_1",
                    "tete_liste_tour_1",
                )
            },
        ),
        (
            "Deuxième tour",
            {
                "fields": (
                    "liste_tour_2",
                    "liste_soutenue_tour_2",
                    "type_soutien_tour_2",
                    "tete_liste_tour_2",
                )
            },
        ),
        (
            "Présence de la campagne sur internet",
            {"fields": ("twitter", "facebook", "website")},
        ),
        (
            "Informations pour les dons par chèque",
            {"fields": ("ordre_don", "adresse_don")},
        ),
        ("Permission", {"fields": ("chefs_file", "municipales2020_people_list")},),
    )

    list_display = (
        "__str__",
        "published",
        "liste_tour_1",
        "liste_tour_2",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
    )

    # doit être True-ish pour déclencher l'utilisation
    search_fields = ("name", "code_departement")
    autocomplete_fields = ("chefs_file",)
    list_filter = (CheffeDeFileFilter, "published")

    def get_absolute_url(self):
        return reverse(
            "view_commune",
            kwargs={"code_departement": self.code_departement, "slug": self.slug},
        )

    def municipales2020_people_list(self, object):
        liste = object.listes.filter(
            soutien__in=[Liste.SOUTIEN_PUBLIC, Liste.SOUTIEN_PREF]
        ).first()

        link_list = format_html(
            '<a href="{}" class="button">Voir toutes les listes dans cette commune</a>',
            f'{reverse("admin:municipales_liste_changelist",)}?q={object.code}',
        )

        if liste is None:
            return link_list

        people = Person.objects.filter(
            coordinates__distance_lt=(object.coordinates, D(m=10000))
        ).search(
            *(
                f"{nom} {prenom}"
                for nom, prenom in zip(liste.candidats_noms, liste.candidats_prenoms)
            )
        )

        return mark_safe(
            "<p>"
            + link_list
            + "</p><p>"
            + format_html_join(
                mark_safe("<br>"),
                "{} {}",
                (
                    (nom, prenom)
                    for nom, prenom in zip(
                        liste.candidats_noms, liste.candidats_prenoms
                    )
                ),
            )
            + "</p><p>"
            + format_html_join(
                mark_safe("<br>"),
                '<a href="{}">{}</a> <a href="{}" class="button">créer un mandat pour cette personne</a>',
                (
                    (
                        reverse("admin:people_person_change", args=[p.pk]),
                        str(p),
                        reverse("admin:elus_mandatmunicipal_add")
                        + f"?person={p.pk}&commune={object.code}",
                    )
                    for p in people
                ),
            )
            + "</p>"
        )

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.search(search_term)

        use_distinct = False
        return queryset, use_distinct

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        # copié depuis super
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        return [
            path("par_insee/<path:insee>/", wrap(self.redirect_from_insee_view))
        ] + super().get_urls()

    def redirect_from_insee_view(self, request, insee):
        info = (self.model._meta.app_label, self.model._meta.model_name)
        commune = get_object_or_404(CommunePage, code=insee)
        return redirect("admin:%s_%s_change" % info, commune.id)


class AvecCommuneFilter(SimpleListFilter):
    title = "Avec ou sans commune"
    parameter_name = "avec_commune"

    def lookups(self, request, model_admin):
        return (("O", "Avec commune"), ("N", "Sans commune"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "O":
            return queryset.exclude(commune=None)
        elif value == "N":
            return queryset.filter(commune=None)
        return queryset


class MetropoleOutremerFilter(SimpleListFilter):
    title = "Métropole ou Outremer"
    parameter_name = "metropole_outremer"
    condition = reduce(or_, (Q(code__startswith=str(i)) for i in range(10)))

    def lookups(self, request, model_admin):
        return (("M", "Métropole seulement"), ("O", "Outremer seulement"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "M":
            return queryset.filter(self.condition)
        elif value == "O":
            return queryset.exclude(self.condition)
        return queryset


@admin.register(Liste)
class ListeAdmin(admin.ModelAdmin):
    readonly_fields = (
        "code",
        "nom",
        "lien_commune",
        "nuance",
        "tete_liste",
        "candidats",
    )

    list_display = ["nom", "lien_commune", "soutien", "nuance", "tete_liste"]
    fields = ["code", "nom", "lien_commune", "soutien", "nuance", "candidats"]

    list_filter = ("nuance", "soutien", AvecCommuneFilter, MetropoleOutremerFilter)

    search_fields = ("nom", "code", "commune__name")

    def candidats(self, obj):
        return mark_safe(
            "<ul>"
            + format_html_join(
                "\n",
                "<li><strong>{}</strong> {} {}</li>",
                (
                    (
                        nom,
                        prenom,
                        "(candidat au conseil communautaire)" if communautaire else "",
                    )
                    for nom, prenom, communautaire in zip(
                        obj.candidats_noms,
                        obj.candidats_prenoms,
                        obj.candidats_communautaire,
                    )
                ),
            )
            + "<ul>"
        )

    def lien_commune(self, object):
        commune = object.commune
        if commune:
            return format_html(
                '<a href="{link}">{name}</a>',
                link=reverse(
                    "admin:municipales_communepage_change", args=(commune.id,)
                ),
                name=str(commune),
            )

    lien_commune.short_description = "Commune"
