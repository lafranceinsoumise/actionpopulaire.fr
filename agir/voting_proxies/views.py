from itertools import chain

from data_france.models import CirconscriptionConsulaire, Commune
from django.conf import settings
from django.core import exceptions
from django.http.response import Http404
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError, Throttled
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response

from agir.lib.export import dict_to_camelcase
from agir.lib.token_bucket import TokenBucket
from agir.lib.utils import get_client_ip
from agir.voting_proxies.actions import (
    get_voting_proxy_requests_for_proxy,
    accept_voting_proxy_requests,
    decline_voting_proxy_requests,
    confirm_voting_proxy_requests,
)
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy
from agir.voting_proxies.serializers import (
    VotingProxyRequestSerializer,
    CommuneOrConsulateSerializer,
    VotingProxySerializer,
    CreateVotingProxySerializer,
)
from agir.voting_proxies.tasks import send_voting_proxy_information_for_request


class CommuneOrConsulateSearchAPIView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
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
    permission_classes = (permissions.AllowAny,)
    queryset = VotingProxyRequest.objects.all()
    serializer_class = VotingProxyRequestSerializer


class VotingProxyCreateAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = VotingProxy.objects.all()
    serializer_class = CreateVotingProxySerializer


class VotingProxyRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = VotingProxy.objects.all()
    serializer_class = VotingProxySerializer


class ReplyToVotingProxyRequestsAPIView(RetrieveUpdateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = VotingProxy.objects.filter(status=VotingProxy.STATUS_CREATED)
    serializer_class = None

    def retrieve(self, request, *args, **kwargs):
        voting_proxy = self.get_object()
        voting_proxy_request_pks = []

        if request.GET.get("vpr", None):
            voting_proxy_request_pks = request.GET.get("vpr").split(",")

        try:
            voting_proxy_requests = get_voting_proxy_requests_for_proxy(
                voting_proxy, voting_proxy_request_pks
            )
        except VotingProxyRequest.DoesNotExist:
            voting_proxy_requests = []

        return Response(
            {
                "firstName": voting_proxy.first_name,
                "requests": [
                    {
                        "id": request.id,
                        "firstName": request.first_name,
                        "pollingStationNumber": request.polling_station_number,
                        "votingDate": dict(VotingProxyRequest.VOTING_DATE_CHOICES)[
                            request.voting_date
                        ],
                        "commune": request.commune.nom if request.commune else None,
                        "consulate": request.consulate.nom
                        if request.consulate
                        else None,
                    }
                    for request in voting_proxy_requests
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


class VotingProxyForRequestRetrieveAPIView(RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = VotingProxyRequest.objects.filter(
        status=VotingProxyRequest.STATUS_ACCEPTED, proxy__isnull=False
    )
    sms_id_bucket = TokenBucket("SendSMSID", 2, 600)
    sms_ip_bucket = TokenBucket("SendSMSIP", 2, 120)

    def throttle_requests(self, request, *args, **kwargs):
        if settings.DEBUG:
            return

        voting_proxy_request_id = kwargs.get("pk")
        client_ip = get_client_ip(request)

        if not self.sms_id_bucket.has_tokens(
            voting_proxy_request_id
        ) or not self.sms_ip_bucket.has_tokens(client_ip):
            raise Throttled(
                detail="Vous avez déjà demandé plusieurs fois l'envoi du message. "
                "Veuillez laisser quelques minutes pour vérifier la bonne réception avant d'en demander d'autres",
                code="throttled",
            )

    def retrieve(self, request, *args, **kwargs):
        self.throttle_requests(request, *args, **kwargs)
        voting_proxy_request = self.get_object()
        send_voting_proxy_information_for_request.delay(voting_proxy_request.pk)
        return Response(status=status.HTTP_202_ACCEPTED)


class VotingProxyRequestConfirmAPIView(UpdateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = VotingProxyRequest.objects.filter(
        status=VotingProxyRequest.STATUS_ACCEPTED, proxy__isnull=False
    )

    def get_voting_proxy_requests(self, data):
        voting_proxy_request_pks = data.get("votingProxyRequests", None)
        try:
            if (
                voting_proxy_request_pks
                and self.queryset.filter(pk__in=voting_proxy_request_pks).exists()
            ):
                return self.queryset.filter(pk__in=voting_proxy_request_pks)

        except exceptions.ValidationError:
            pass

        raise ValidationError(
            {
                "votingProxyRequests": "La valeur de ce champ est obligatoire et devrait être une liste de uuids"
            }
        )

    def update(self, request, *args, **kwargs):
        voting_proxy_requests = self.get_voting_proxy_requests(request.data)
        confirm_voting_proxy_requests(voting_proxy_requests)
        return Response(status=status.HTTP_200_OK)
