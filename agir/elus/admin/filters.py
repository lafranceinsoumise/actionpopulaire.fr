from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Exists, OuterRef, Subquery, Func
from django.utils import timezone

from agir.authentication.models import Role
from agir.elus.models import (
    MandatMunicipal,
    CHAMPS_ELUS_PARRAINAGES,
    RechercheParrainage,
    Scrutin,
    Autorisation,
)
from agir.lib.admin.autocomplete_filter import (
    AutocompleteRelatedModelFilter,
    SelectRelatedModelFilter,
)


class ConseilFilter(AutocompleteRelatedModelFilter):
    field_name = "conseil"
    title = "Commune d'élection"


class DepartementFilter(SelectRelatedModelFilter):
    field_name = "conseil__departement"
    title = "Département"


class DepartementRegionFilter(SelectRelatedModelFilter):
    field_name = "conseil__departement__region"
    title = "Région"


class RegionFilter(SelectRelatedModelFilter):
    field_name = "conseil__region"
    title = "Région"


class CommunautaireFilter(SimpleListFilter):
    parameter_name = "communautaire"
    title = "Par type de mandat communautaire"

    def lookups(self, request, model_admin):
        return [
            *MandatMunicipal.MANDAT_EPCI_CHOICES,
            ("AVEC", "Tous les mandats communautaire"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "AVEC":
            return queryset.exclude(
                communautaire=MandatMunicipal.MANDAT_EPCI_PAS_DE_MANDAT
            )
        elif self.value() in {v for v, l in MandatMunicipal.MANDAT_EPCI_CHOICES}:
            return queryset.filter(communautaire=self.value())
        return queryset


class DatesFilter(SimpleListFilter):
    parameter_name = "dates"
    title = "Dates du mandat"

    def lookups(self, request, model_admin):
        return [
            ("O", "Mandats en cours seulement"),
            ("P", "Mandats passés seulement"),
            ("F", "Mandats non commencés seulement"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "O":
            return queryset.filter(dates__contains=timezone.now().date())
        elif value == "P":
            return queryset.filter(dates__endswith__lte=timezone.now().date())
        elif value == "F":
            return queryset.filter(dates__startswith__gt=timezone.now().date())
        return queryset


class AppelEluFilter(SimpleListFilter):
    title = "2022 Appel élu⋅es"
    parameter_name = "2022_appel_elus"

    def lookups(self, request, model_admin):
        return (
            ("O", "Signé appel élu"),
            ("N", "Pas signé appel élu"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "O":
            return queryset.exclude(
                person__meta__subscriptions__NSP__mandat__isnull=True
            )
        elif value == "N":
            return queryset.filter(
                person__meta__subscriptions__NSP__mandat__isnull=True
            )
        return queryset


class ReferenceFilter(SimpleListFilter):
    parameter_name = "reference"
    title = "Fiche RNE"

    def lookups(self, request, model_admin):
        return (
            ("O", "Avec fiche RNE"),
            ("N", "Sans fiche RNE"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(reference__isnull=value == "N")
        return queryset


class MandatsFilter(SimpleListFilter):
    parameter_name = "mandats"
    title = "Mandats associés aux fiches"

    def lookups(self, request, model_admin):
        return (
            ("O", "Avec un mandat référencé"),
            ("D", "Avec plus d'un mandat référencé (doublon)"),
            ("N", "Sans mandat référencé"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "D":
            return queryset.annotate(n=Count("elu")).filter(n__gt=1)
        elif value in ["O", "N"]:
            return queryset.annotate(
                avec_mandat=Exists(
                    MandatMunicipal.objects.filter(reference_id=OuterRef("id"))
                )
            ).filter(avec_mandat=value == "O")
        return queryset


class ParrainagesFilter(SimpleListFilter):
    parameter_name = "parrainage"
    title = "Parrainage pour 2022"

    def lookups(self, request, model_admin):
        return (
            ("O", "Avec un parrainage confirmé"),
            ("N", "Sans parrainage pour le moment"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "O":
            return queryset.filter(
                reference__parrainage__statut=RechercheParrainage.Statut.VALIDEE
            )
        elif value == "N":
            return queryset.exclude(
                reference__parrainage__statut=RechercheParrainage.Statut.VALIDEE
            )

        return queryset


class TypeEluFilter(SimpleListFilter):
    parameter_name = "type-elu"
    title = "Type d'élu·e"

    def lookups(self, request, model_admin):
        return (
            (f, model_admin.model._meta.get_field(f).verbose_name)
            for f in CHAMPS_ELUS_PARRAINAGES
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value in CHAMPS_ELUS_PARRAINAGES:
            return queryset.filter(**{f"{value}__isnull": False})
        return queryset


class ScrutinFilter(SimpleListFilter):
    """Filtre les résultats aussi bien pour n'afficher qu'un scrutin et limiter les candidats affichés.

    Ce filtre a un rôle particulièrement important parce qu'il applique aussi les permissions de l'utilisateur
    pour limiter les scrutins accessibles, et pour chaque scrutin, les candidatures visibles.

    Ce n'est pas l'endroit idéal pour le faire, mais c'est le seul endroit où il est possible de le faire sans
    multiplier les requêtes. En effet, je ne voyais pas trop d'autre solution pour écrire la requête pour filtrer
    les circonscriptions visibles sans avoir accès au scrutin sélectionné dans ce filtre, à cause de la clé étrangère
    générique.
    """

    parameter_name = "scrutin"
    title = "Scrutin"

    def lookups(self, request, model_admin):
        role: Role = request.user

        scrutins = Scrutin.objects.select_related("circonscription_content_type")
        if role.has_perm("elus.view_candidature"):
            scrutins = list(scrutins)
        else:
            scrutins = list(
                scrutins.filter(
                    id__in=Subquery(
                        Autorisation.objects.filter(groupe__user=role).values(
                            "scrutin_id"
                        )
                    )
                )
            )

        if not scrutins:
            self.default_id = None
            return ()

        self.content_types = {s.id: s.circonscription_content_type for s in scrutins}
        self.default_id = scrutins[0].id

        return (
            ("", scrutins[0].nom),
            *((str(s.id), s.nom) for s in scrutins[1:]),
        )

    def queryset(self, request, queryset):
        value = self.value()

        try:
            id = int(value)
        except (ValueError, TypeError):
            if self.default_id is None:
                return queryset.none()
            id = self.default_id

        if id not in self.content_types:
            return queryset.none()

        content_type = self.content_types[id]
        circonscription_qs = content_type.model_class()._default_manager.all()
        role: Role = request.user

        qs = queryset.filter(scrutin_id=id).annotate(
            code_circonscription=Subquery(
                circonscription_qs.filter(
                    id=OuterRef("circonscription_object_id")
                ).values("code")[:1]
            ),
        )

        # dans le cas où l'utilisateur n'a pas de permission générique pour voir les candidatures, on trie le queryset
        # pour n'inclure que celles dans des circonscriptions qui le concernent, désignées via des autorisations.
        if not role.has_perm("elus.view_candidature"):
            qs = qs.annotate(
                autorisation=Exists(
                    Autorisation.objects.filter(
                        groupe__user=role,
                        scrutin_id=id,
                        prefixes__overlap=Func(
                            OuterRef("code_circonscription"), function="prefixes_array"
                        ),
                    )
                ),
            ).filter(autorisation=True)

        return qs

    def choices(self, changelist):
        it = super().choices(changelist)

        # ne pas renvoyer le premier choix "vide" renvoyé
        next(it)
        yield from it
