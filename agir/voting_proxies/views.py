from itertools import chain

from data_france.models import CirconscriptionConsulaire, Commune
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.voting_proxies.models import VotingProxyRequest
from agir.voting_proxies.serializers import (
    VotingProxyRequestSerializer,
    CommuneOrConsulateSerializer,
)


class CommuneOrConsulateSearchAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommuneOrConsulateSerializer
    search_term_param = "q"

    def list(self, request, *args, **kwargs):
        search_term = request.GET.get(self.search_term_param)
        consulates = CirconscriptionConsulaire.objects.search(search_term)
        communes = self.filter_queryset(
            Commune.objects.filter(
                type__in=(Commune.TYPE_COMMUNE, Commune.TYPE_ARRONDISSEMENT_PLM),
            )
            .exclude(code__in=("75056", "69123", "13055"))
            .search(search_term)
        )
        queryset = sorted(
            list(chain(communes, consulates)), key=lambda result: result.rank
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VotingProxyRequestCreateAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = VotingProxyRequest.objects.all()
    serializer_class = VotingProxyRequestSerializer
