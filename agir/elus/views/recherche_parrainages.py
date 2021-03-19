from data_france.models import EluMunicipal
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import Distance as D
from django.db.models import (
    Q,
    Case,
    When,
    OuterRef,
    Subquery,
    CharField,
    Value,
    Exists,
    IntegerField,
)
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.elus.models import RechercheParrainageMaire, StatutRechercheParrainage
from agir.elus.serializers import (
    EluMunicipalSerializer,
    ModifierRechercheSerializer,
    CreerRechercheSerializer,
    CRITERE_INCLUSION_ELUS,
)
from agir.lib.rest_framework_permissions import (
    IsPersonPermission,
    HasSpecificPermissions,
)

ID_RECHERCHE_PARRAINAGE_SUBQUERY = Subquery(
    RechercheParrainageMaire.objects.filter(elu_id=OuterRef("id")).values("id")[:1]
)


def queryset_elus(person):
    qs = (
        EluMunicipal.objects.filter(CRITERE_INCLUSION_ELUS)
        .select_related("commune")
        .annotate(
            statut=Coalesce(
                Subquery(
                    RechercheParrainageMaire.objects.filter(elu_id=OuterRef("id"))
                    .bloquant()
                    .annotate(
                        statut_composite=Case(
                            When(
                                Q(person_id=person.id)
                                & ~Q(statut=StatutRechercheParrainage.EN_COURS),
                                then=Value(
                                    EluMunicipalSerializer.Statut.PERSONNELLEMENT_VU
                                ),
                            ),
                            When(
                                ~Q(statut=StatutRechercheParrainage.EN_COURS),
                                then=Value(EluMunicipalSerializer.Statut.TERMINE),
                            ),
                            When(
                                person_id=person.id,
                                then=Value(EluMunicipalSerializer.Statut.A_CONTACTER),
                            ),
                            default=Value(EluMunicipalSerializer.Statut.EN_COURS),
                            output_field=CharField(),
                        ),
                    )
                    .values("statut_composite")[:1]
                ),
                Value(EluMunicipalSerializer.Statut.DISPONIBLE),
            ),
            recherche_parrainage_maire_id=Case(
                When(
                    Q(statut=EluMunicipalSerializer.Statut.A_CONTACTER),
                    ID_RECHERCHE_PARRAINAGE_SUBQUERY,
                ),
                default=None,
            ),
        )
    )

    if person.coordinates is not None:
        qs = qs.annotate(distance=Distance("commune__geometry", person.coordinates),)

    return qs


class RechercheParrainagesView(
    SoftLoginRequiredMixin, PermissionRequiredMixin, TemplateView
):
    template_name = "elus/parrainages/page.html"
    permission_required = "elus.acces_parrainages"

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        if person.coordinates is None:
            return super().get_context_data(**kwargs, elus=[],)

        a_contacter_qs = (
            EluMunicipal.objects.filter(CRITERE_INCLUSION_ELUS)
            .select_related("commune")
            .filter(
                rechercher_parrainage__statut=RechercheParrainageMaire.Statut.EN_COURS,
                rechercher_parrainage__person_id=person.id,
            )
            .annotate(
                statut=Value(
                    EluMunicipalSerializer.Statut.A_CONTACTER, output_field=CharField()
                ),
                distance=Distance("commune__geometry", person.coordinates),
                recherche_parrainage_maire_id=ID_RECHERCHE_PARRAINAGE_SUBQUERY,
            )
        )
        elus_proches_qs = (
            EluMunicipal.objects.filter(CRITERE_INCLUSION_ELUS)
            .select_related("commune")
            .annotate(
                statut=Value(
                    EluMunicipalSerializer.Statut.DISPONIBLE, output_field=CharField()
                ),
                recherche_parrainage_maire_id=Value(None, output_field=IntegerField()),
                distance=Distance("commune__geometry", person.coordinates),
                pris=Exists(
                    RechercheParrainageMaire.objects.filter(
                        elu_id=OuterRef("id")
                    ).bloquant()
                ),
            )
            .filter(
                pris=False,
                commune__geometry__dwithin=(
                    person.coordinates,
                    D(km=20),
                ),  # force l'utilisation de l'index géographique
            )
            .order_by("distance")[:10]
        )

        elus_a_contacter = EluMunicipalSerializer(a_contacter_qs, many=True).data
        elus_proches = EluMunicipalSerializer(elus_proches_qs, many=True).data

        return super().get_context_data(
            **kwargs, elus={"aContacter": elus_a_contacter, "proches": elus_proches},
        )


class AccesParrainagePermission(HasSpecificPermissions):
    permissions = ["elus.acces_parrainages"]


class ChercherEluView(ListAPIView):
    permission_classes = (IsPersonPermission, AccesParrainagePermission)
    serializer_class = EluMunicipalSerializer

    def get_queryset(self):
        search_terms = self.request.query_params.get("q")
        if not search_terms or len(search_terms) < 3:
            return EluMunicipal.objects.none()

        return queryset_elus(self.request.user.person).search(search_terms)[:20]


class CreerRechercheParrainageView(CreateAPIView):
    permission_classes = (IsPersonPermission, AccesParrainagePermission)
    serializer_class = CreerRechercheSerializer


class ModifierRechercheParrainageView(UpdateAPIView):
    permission_classes = (IsPersonPermission, AccesParrainagePermission)
    serializer_class = ModifierRechercheSerializer

    def get_queryset(self):
        return RechercheParrainageMaire.objects.filter(
            person=self.request.user.person,
            statut=RechercheParrainageMaire.Statut.EN_COURS,
        )
