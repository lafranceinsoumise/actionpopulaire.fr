from agir.gestion.models import Projet, Depense
from django.contrib.admin import SimpleListFilter, ListFilter


class InclureProjetsMilitantsFilter(ListFilter):
    parameter_name = "militant"
    title = "origine du projet"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        if self.parameter_name in params:
            self.value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = self.value
        else:
            self.value = None

    def expected_parameters(self):
        return [self.parameter_name]

    def has_output(self):
        return True

    def choices(self, changelist):
        yield {
            "selected": self.value is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": "n'inclure que les projets créés dans l'administration",
        }
        yield {
            "selected": self.value == "O",
            "query_string": changelist.get_query_string({self.parameter_name: "O"}),
            "display": "inclure aussi les projets militants",
        }

    def queryset(self, request, queryset):
        if self.value == "O":
            return queryset
        return queryset.filter(origine=Projet.Origin.ADMINISTRATION)


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
