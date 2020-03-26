from django import forms
from django.contrib.gis.measure import D
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from functools import reduce, update_wrapper

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.urls import reverse, path
from operator import or_

from agir.api.admin import admin_site
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
            return queryset.exclude(municipales2020_admins=None)
        elif value == "N":
            return queryset.filter(municipales2020_admins=None)
        return queryset


class CommuneForm(forms.ModelForm):
    liste_soutenue = forms.ModelChoiceField(
        label="Liste soutenue par la Fi",
        queryset=Liste.objects.none(),
        empty_label="Aucune",
        required=False,
    )
    type_soutien = forms.ChoiceField(
        label="Type de soutien",
        choices=[
            (Liste.SOUTIEN_PUBLIC, "Soutien public"),
            (Liste.SOUTIEN_PREF, "Simple préférence"),
        ],
        initial="P",
        required="P",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        listes = self.instance.listes.all()

        self.fields["liste_soutenue"].queryset = listes

        try:
            self.liste_soutenue = listes.exclude(soutien=Liste.SOUTIEN_NON).get()
            self.fields["liste_soutenue"].initial = self.liste_soutenue
            self.fields["type_soutien"].initial = self.liste_soutenue.soutien
        except Liste.DoesNotExist:
            self.liste_soutenue = None

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


@admin.register(CommunePage, site=admin_site)
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
            "Informations sur la campagne",
            {
                "fields": (
                    "published",
                    "strategy",
                    "liste_soutenue",
                    "type_soutien",
                    "tete_liste",
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
            "Présence de la campagne sur internet",
            {"fields": ("twitter", "facebook", "website")},
        ),
        (
            "Informations pour les dons par chèque",
            {"fields": ("ordre_don", "adresse_don")},
        ),
        (
            "Permission",
            {"fields": ("municipales2020_admins", "municipales2020_people_list")},
        ),
    )

    list_display = (
        "__str__",
        "published",
        "strategy",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
        "twitter",
        "facebook",
        "website",
    )
    list_editable = (
        "published",
        "strategy",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
    )

    # doit être True-ish pour déclencher l'utilisation
    search_fields = ("name", "code_departement")
    autocomplete_fields = ("municipales2020_admins",)
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
                "<br>",
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
                "<br>",
                '<a href="{}">{}</a>',
                (
                    (reverse("admin:people_person_change", args=[p.pk]), str(p))
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


@admin.register(Liste, site=admin_site)
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
