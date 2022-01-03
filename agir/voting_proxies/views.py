from itertools import chain

from data_france.models import CirconscriptionConsulaire, Commune
from django.core import exceptions
from django.db import transaction
from django.http.response import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.lib.export import dict_to_camelcase
from agir.voting_proxies.actions import (
    get_voting_proxy_requests_for_proxy,
    accept_voting_proxy_requests,
    decline_voting_proxy_requests,
)
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy
from agir.voting_proxies.serializers import (
    VotingProxyRequestSerializer,
    CommuneOrConsulateSerializer,
    VotingProxySerializer,
    CreateVotingProxySerializer,
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


class VotingProxyCreateAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = VotingProxy.objects.all()
    serializer_class = CreateVotingProxySerializer


class VotingProxyRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = VotingProxy.objects.all()
    serializer_class = VotingProxySerializer


class ReplyToVotingProxyRequestsAPIViex(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = VotingProxy.objects.filter(status=VotingProxy.STATUS_AVAILABLE)
    serializer_class = None

    def retrieve(self, request, *args, **kwargs):
        voting_proxy = self.get_object()
        voting_proxy_request_pks = request.GET.getlist("vpr", [])
        try:
            voting_proxy_requests = get_voting_proxy_requests_for_proxy(
                voting_proxy, voting_proxy_request_pks
            )
        except VotingProxyRequest.DoesNotExist:
            raise Http404

        return Response(
            {
                "firstName": voting_proxy.first_name,
                "requests": [
                    dict_to_camelcase(voting_proxy_request)
                    for voting_proxy_request in voting_proxy_requests
                ],
            }
        )

    def clean(self, data):
        voting_proxy = self.get_object()
        is_available = data.get("isAvailable", None)
        voting_proxy_request_pks = data.get("votingProxyRequests", None)
        voting_proxy_requests = []
        errors = {}

        if not isinstance(is_available, bool):
            errors[
                "isAvailable"
            ] = "La valeur de ce champ est obligatoire et devrait être un booléan"

        if not voting_proxy_request_pks:
            errors[
                "votingProxyRequests"
            ] = "La valeur de ce champ est obligatoire et devrait être une liste de uuids"
        else:
            try:
                voting_proxy_requests = get_voting_proxy_requests_for_proxy(
                    voting_proxy, voting_proxy_request_pks
                )
            except (VotingProxyRequest.DoesNotExist, exceptions.ValidationError):
                errors["votingProxyRequests"] = "La valeur de ce champ n'est pas valide"

        if errors.keys():
            raise ValidationError(errors)

        return {
            "is_available": is_available,
            "voting_proxy": voting_proxy,
            "voting_proxy_requests": voting_proxy_requests,
        }

    def update(self, request, *args, **kwargs):
        validated_data = self.clean(request.data)
        is_available = validated_data.pop("is_available")

        if is_available:
            accept_voting_proxy_requests(**validated_data)
        else:
            decline_voting_proxy_requests(**validated_data)

        return Response(
            {
                "firstName": validated_data["voting_proxy"].first_name,
                "status": validated_data["voting_proxy"].status,
            }
        )
