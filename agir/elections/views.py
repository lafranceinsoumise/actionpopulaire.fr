from itertools import chain

from data_france.models import CirconscriptionConsulaire, Commune
from django.conf import settings
from rest_framework import permissions
from rest_framework.exceptions import Throttled
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from agir.elections.models import PollingStationOfficer
from agir.elections.serializers import (
    VotingCommuneOrConsulateSerializer,
    CreateUpdatePollingStationOfficerSerializer,
)
from agir.lib.rest_framework_permissions import IsActionPopulaireClientPermission
from agir.lib.token_bucket import TokenBucket
from agir.lib.utils import get_client_ip


class VotingCommuneOrConsulateSearchAPIView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = VotingCommuneOrConsulateSerializer
    search_term_param = "q"

    def list(self, request, *args, **kwargs):
        search_term = request.GET.get(self.search_term_param)
        consulates = CirconscriptionConsulaire.objects.search(search_term)[:20]
        communes = self.filter_queryset(
            Commune.objects.filter(
                type__in=(Commune.TYPE_COMMUNE, Commune.TYPE_ARRONDISSEMENT_PLM),
            )
            .exclude(code__in=("75056", "69123", "13055"))
            .search(search_term)[:20]
        )
        queryset = sorted(
            list(chain(communes, consulates)), key=lambda result: result.rank
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


create_polling_station_officer_ip_bucket = TokenBucket(
    "CreatePollingStationOfficerIP", 2, 600
)
create_polling_station_officer_email_bucket = TokenBucket(
    "CreatePollingStationOfficerEMAIL", 2, 600
)


class RetrieveCreatePollingStationOfficerAPIView(RetrieveAPIView, CreateAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = PollingStationOfficer.objects.all()
    serializer_class = CreateUpdatePollingStationOfficerSerializer
    messages = {
        "throttled": "Vous avez déjà fais plusieurs demandes. Veuillez laisser quelques minutes "
        "avant d'en faire d'autres."
    }

    def throttle_requests(self, data):
        if settings.DEBUG:
            return

        client_ip = get_client_ip(self.request)
        if not create_polling_station_officer_ip_bucket.has_tokens(client_ip):
            raise Throttled(detail=self.messages["throttled"], code="throttled")

        email = data.get("email", None)
        if email and not create_polling_station_officer_email_bucket.has_tokens(email):
            raise Throttled(detail=self.messages["throttled"], code="throttled")

    def perform_create(self, serializer):
        # TODO: Restore throttling !
        # self.throttle_requests(serializer.validated_data)
        super().perform_create(serializer)

    def retrieve(self, request, *args, **kwargs):
        data = None
        if request.user.is_authenticated and request.user.person is not None:
            try:
                data = request.user.person.polling_station_officer
                data = self.get_serializer(data)
            except PollingStationOfficer.DoesNotExist:
                pass
        return Response(data)
