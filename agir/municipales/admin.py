from functools import reduce, update_wrapper
from operator import or_

from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, path
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from agir.municipales.models import CommunePage, Liste


def presentation_liste(liste):
    code = liste.commune.code
    people = liste.obtenir_comptes_candidats()

    liste_candidats = format_html_join(
        mark_safe("<br>"),
        "{} {}",
        (
            (nom, prenom)
            for nom, prenom in zip(liste.candidats_noms, liste.candidats_prenoms)
        ),
    )

    liste_comptes = format_html_join(
        mark_safe("<br>"),
        '<a href="{}">{}</a> <a href="{}" class="button">créer un mandat pour cette personne</a>',
        (
            (
                reverse("admin:people_person_change", args=[p.pk]),
                str(p),
                reverse("admin:elus_mandatmunicipal_add")
                + f"?person={p.pk}&commune={code}",
            )
            for p in people
        ),
    )

    return format_html(
        "<p>{liste_candidats}</p><p>{liste_comptes}</p>",
        liste_candidats=liste_candidats,
        liste_comptes=liste_comptes,
    )


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

    TOURS = [
        (1, "liste_soutenue_tour_1", "type_soutien_tour_1"),
        (2, "liste_soutenue_tour_2", "type_soutien_tour_2"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for tour, liste_soutenue_f, type_soutien_f in self.TOURS:
            listes = self.instance.listes.filter(tour=tour)

            self.fields[liste_soutenue_f].queryset = listes
            try:
                liste_actuelle = listes.exclude(soutien=Liste.SOUTIEN_NON).get()
            except Liste.DoesNotExist:
                setattr(self, liste_soutenue_f, None)
            else:
                setattr(self, liste_soutenue_f, liste_actuelle)
                self.fields[liste_soutenue_f].initial = liste_actuelle
                self.fields[type_soutien_f].initial = liste_actuelle.soutien

    def _save_m2m(self):
        super()._save_m2m()

        for _, liste_soutenue_f, type_soutien_f in self.TOURS:
            nouvelle_liste_soutenue = self.cleaned_data[liste_soutenue_f]

            if (
                liste_soutenue_f in self.changed_data
                or type_soutien_f in self.changed_data
            ):
                with transaction.atomic():
                    liste_actuelle = getattr(self, liste_soutenue_f, None)
                    if (
                        liste_actuelle is not None
                        and liste_actuelle != nouvelle_liste_soutenue
                    ):
                        self.liste_soutenue.soutien = Liste.SOUTIEN_NON
                        self.liste_soutenue.save(update_fields=["soutien"])

                    if nouvelle_liste_soutenue is not None:
                        nouvelle_liste_soutenue.soutien = self.cleaned_data[
                            type_soutien_f
                        ]
                        nouvelle_liste_soutenue.save(update_fields=["soutien"])


@admin.register(CommunePage)
class CommunePageAdmin(admin.ModelAdmin):
    form = CommuneForm
    readonly_fields = (
        "code",
        "code_departement",
        "name",
        "candidats_liste_tour_1",
        "candidats_liste_tour_2",
        "toutes_les_listes",
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
                    "candidats_liste_tour_1",
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
                    "candidats_liste_tour_2",
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
        (
            "Permission",
            {"fields": ("chefs_file", "toutes_les_listes")},
        ),
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

    def candidats_liste_tour_1(self, object):
        liste_tour_1 = object.listes.filter(
            soutien__in=[Liste.SOUTIEN_PUBLIC, Liste.SOUTIEN_PREF], tour=1
        ).first()

        if liste_tour_1 is None:
            return ""
        return presentation_liste(liste_tour_1)

    candidats_liste_tour_1.short_description = "Liste soutenue au 1er tour"

    def candidats_liste_tour_2(self, object):
        liste_tour_2 = object.listes.filter(
            soutien__in=[Liste.SOUTIEN_PUBLIC, Liste.SOUTIEN_PREF], tour=2
        ).first()

        if liste_tour_2 is None:
            return ""
        return presentation_liste(liste_tour_2)

    candidats_liste_tour_2.short_description = "Liste soutenue au 2ème tour"

    def toutes_les_listes(self, object):
        return format_html(
            '<a href="{}" class="button">Voir toutes les listes dans cette commune</a>',
            f'{reverse("admin:municipales_liste_changelist",)}?q={object.code}',
        )

    toutes_les_listes.short_description = "Autres listes"

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
        "tour",
        "nuance",
        "tete_liste",
        "candidats",
    )

    list_display = ["nom", "lien_commune", "tour", "soutien", "nuance", "tete_liste"]
    fields = ["code", "nom", "lien_commune", "tour", "soutien", "nuance", "candidats"]

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
