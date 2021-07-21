from agir.gestion.models import Projet, Depense
from django.contrib.admin import SimpleListFilter


class ProjetResponsableFilter(SimpleListFilter):
    parameter_name = "responsable"
    title = "responsable actuel"

    def lookups(self, request, model_admin):
        return (("R", "Responsable du compte"), ("G", "Gestionnaire projets"))

    def queryset(self, request, queryset):
        value = self.value()

        if value == "R":
            return queryset.filter(etat=Projet.Etat.FINALISE)
        elif value == "G":
            return queryset.filter(
                etat__in=[
                    Projet.Etat.CREE_PLATEFORME,
                    Projet.Etat.EN_CONSTITUTION,
                    Projet.Etat.RENVOI,
                ]
            )
        return queryset


class DepenseResponsableFilter(SimpleListFilter):
    parameter_name = "responsable"
    title = "responsable actuel"

    def lookups(self, request, model_admin):
        return (("R", "Responsable du compte"), ("G", "Gestionnaire projets"))

    def queryset(self, request, queryset):
        value = self.value()

        if value == "R":
            return queryset.filter(
                etat__in=[Depense.Etat.ATTENTE_ENGAGEMENT, Depense.Etat.COMPLET]
            )
        elif value == "G":
            return queryset.filter(
                etat__in=[Depense.Etat.ATTENTE_VALIDATION, Depense.Etat.CONSTITUTION]
            )

        return queryset
