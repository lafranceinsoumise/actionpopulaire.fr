import reversion
from data_france.models import EluMunicipal, CodePostal
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.gis.db.models import Union, MultiPolygonField
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
)
from django.db.models.functions import Coalesce, Cast
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from rest_framework.generics import (
    ListAPIView,
    UpdateAPIView,
    CreateAPIView,
    get_object_or_404,
)

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.elus.forms import DemandeAccesApplicationParrainagesForm
from agir.elus.models import (
    RechercheParrainage,
    StatutRechercheParrainage,
    AccesApplicationParrainages,
)
from agir.elus.serializers import (
    EluMunicipalSerializer,
    ModifierRechercheSerializer,
    CreerRechercheSerializer,
    CRITERE_INCLUSION_ELUS,
)
from agir.front.view_mixins import ReactBaseView
from agir.lib.rest_framework_permissions import (
    IsPersonPermission,
    HasSpecificPermissions,
)

ID_RECHERCHE_PARRAINAGE_SUBQUERY = Subquery(
    RechercheParrainage.objects.filter(
        maire_id=OuterRef("id"), statut=RechercheParrainage.Statut.EN_COURS
    ).values("id")[:1]
)


def queryset_elus(person, distance_geom=None):
    qs = (
        EluMunicipal.objects.filter(CRITERE_INCLUSION_ELUS)
        .select_related("commune")
        .annotate(
            statut=Coalesce(
                Subquery(
                    RechercheParrainage.objects.filter(maire_id=OuterRef("id"))
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

    if distance_geom is not None:
        qs = qs.annotate(distance=Distance("commune__geometry", distance_geom),)

    return qs


def queryset_elus_proches(person, geom):
    return (
        queryset_elus(person, geom)
        .filter(
            commune__geometry__dwithin=(
                geom,
                D(km=20),
            ),  # force l'utilisation de l'index géographique
        )
        .order_by("distance")
    )


class RechercheParrainagesView(
    SoftLoginRequiredMixin, PermissionRequiredMixin, ReactBaseView
):
    bundle_name = "elus/parrainages"
    app_mount_id = "app"

    permission_required = "elus.acces_parrainages"

    def handle_no_permission(self):
        messages.add_message(
            self.request,
            messages.WARNING,
            "Vous n'avez pas encore l'accès à l'application de parrainages : il vous faut d'abord remplir le formulaire ci-dessous.",
        )
        return HttpResponseRedirect(reverse("elus:demande_acces_parrainages"))

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        if person.coordinates is None:
            return super().get_context_data(**kwargs, elus=[],)

        # il est nécessaire de rajouter la condition à la main pour espérer des requêtes sans seq scan
        a_contacter_qs = queryset_elus(person, person.coordinates).filter(
            parrainage__statut=StatutRechercheParrainage.EN_COURS,
            parrainage__person_id=person.id,
        )

        elus_proches_qs = queryset_elus_proches(person, person.coordinates).filter(
            statut=EluMunicipalSerializer.Statut.DISPONIBLE
        )[:20]

        elus_a_contacter = EluMunicipalSerializer(a_contacter_qs, many=True).data
        elus_proches = EluMunicipalSerializer(elus_proches_qs, many=True).data

        return super().get_context_data(
            **kwargs,
            export_data={"aContacter": elus_a_contacter, "proches": elus_proches},
            data_script_id="elusInitiaux",
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


class ChercherCodePostalView(ListAPIView):
    permission_classes = (IsPersonPermission, AccesParrainagePermission)
    serializer_class = EluMunicipalSerializer

    def get_queryset(self):
        code_postal = get_object_or_404(CodePostal, code=self.kwargs["code"])
        geom = code_postal.communes.aggregate(
            geom=Union(
                Cast("geometry", output_field=MultiPolygonField(geography=False))
            )
        )["geom"]

        if geom:
            return queryset_elus_proches(self.request.user.person, geom).filter(
                commune__geometry__dwithin=(geom, D(km=5),)
            )
        return EluMunicipal.objects.none()


class CreerRechercheParrainageView(CreateAPIView):
    permission_classes = (IsPersonPermission, AccesParrainagePermission)
    serializer_class = CreerRechercheSerializer


class ModifierRechercheParrainageView(UpdateAPIView):
    permission_classes = (IsPersonPermission, AccesParrainagePermission)
    serializer_class = ModifierRechercheSerializer

    def get_queryset(self):
        return RechercheParrainage.objects.filter(
            person=self.request.user.person,
            statut=StatutRechercheParrainage.EN_COURS,
            maire__isnull=False,
        )


class DemandeAccesParrainagesView(SoftLoginRequiredMixin, FormView):
    form_class = DemandeAccesApplicationParrainagesForm
    template_name = "elus/parrainages/demande-acces.html"
    success_url = reverse_lazy("dashboard")

    def get(self, request, *args, **kwargs):
        if self.request.user.has_perm("elus.acces_parrainages"):
            return HttpResponseRedirect(reverse("elus:parrainages"))
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user.person
        return kwargs

    def form_valid(self, form):
        form.save()

        with reversion.create_revision():
            reversion.set_user(self.request.user)
            reversion.set_comment("Demande d'accès à l'application de parrainage")

            AccesApplicationParrainages.objects.get_or_create(
                person=self.request.user.person,
                defaults={"etat": AccesApplicationParrainages.Etat.EN_ATTENTE},
            )

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre demande a été enregistrée et sera étudiée avant validation.",
        )

        return super().form_valid(form)
