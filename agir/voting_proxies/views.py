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

from agir.lib.rest_framework_permissions import (
    IsActionPopulaireClientPermission,
    GlobalOrObjectPermissions,
)
from agir.lib.token_bucket import TokenBucket
from agir.lib.utils import get_client_ip, front_url
from agir.voting_proxies.actions import (
    get_voting_proxy_requests_for_proxy,
    accept_voting_proxy_requests,
    mark_voting_proxy_as_unavailable,
    confirm_voting_proxy_requests,
    cancel_voting_proxy_requests,
    cancel_voting_proxy_request_acceptation,
    accept_single_voting_proxy_request,
    get_acceptable_voting_proxy_requests_for_proxy,
)
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy
from agir.voting_proxies.serializers import (
    VotingProxyRequestSerializer,
    VotingProxySerializer,
    AcceptedVotingProxyRequestSerializer,
    CreateVotingProxySerializer,
)
from agir.voting_proxies.tasks import send_voting_proxy_information_for_request

create_voter_ip_bucket = TokenBucket("CreateVoterIP", 2, 600)
create_voter_email_bucket = TokenBucket("CreateVoterEMAIL", 2, 600)


class CreateVoterAPIView(CreateAPIView):
    messages = {
        "throttled": "Vous avez déjà fais plusieurs demandes. Veuillez laisser quelques minutes "
        "avant d'en faire d'autres."
    }

    def throttle_requests(self, data):
        if settings.DEBUG:
            return

        client_ip = get_client_ip(self.request)
        if not create_voter_ip_bucket.has_tokens(client_ip):
            raise Throttled(detail=self.messages["throttled"], code="throttled")

        email = data.get("email", None)
        if email and not create_voter_email_bucket.has_tokens(email):
            raise Throttled(detail=self.messages["throttled"], code="throttled")

    def perform_create(self, serializer):
        self.throttle_requests(serializer.validated_data)
        super().perform_create(serializer)


class VotingProxyRequestCreateAPIView(CreateVoterAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = VotingProxyRequest.objects.all()
    serializer_class = VotingProxyRequestSerializer


class VotingProxyRequestRetrieveUpdatePermission(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "PUT": [], "PATCH": []}
    object_perms_map = {
        "GET": ["voting_proxies.view_voting_proxy_request"],
        "PUT": ["voting_proxies.view_voting_proxy_request"],
        "PATCH": ["voting_proxies.view_voting_proxy_request"],
    }


class VotingProxyRequestRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        IsActionPopulaireClientPermission,
        VotingProxyRequestRetrieveUpdatePermission,
    )
    queryset = VotingProxyRequest.objects.all()
    serializer_class = AcceptedVotingProxyRequestSerializer

    def clean_voting_proxy(self, voting_proxy_id):
        voting_proxy_request = self.get_object()
        voting_proxy = VotingProxy.objects.filter(id=voting_proxy_id).first()

        if (
            voting_proxy is not None
            and voting_proxy.is_available()
            and voting_proxy_request.email != voting_proxy.email
            and voting_proxy_request.voting_date.strftime("%Y-%m-%d")
            in voting_proxy.available_voting_dates
        ):
            return voting_proxy

        raise ValidationError(
            detail={
                "votingProxy": "Le volontaire indiqué n'a pas été trouvé ou ne peut pas prendre de procurations de vote."
            }
        )

    def clean(self):
        data = self.request.data
        if data.get("action", None) == "accept":
            action = accept_single_voting_proxy_request
        elif data.get("action", None) == "decline":
            action = mark_voting_proxy_as_unavailable
        else:
            raise ValidationError(
                detail={"action": "La valeur de ce champ n'est pas valide"}
            )

        return {"action": action}

    def retrieve(self, request, *args, **kwargs):
        try:
            self.clean_voting_proxy(request.GET.get("vp", None))
        except ValidationError as e:
            self.permission_denied(request, message=str(e))

        voting_proxy_request = self.get_object()
        serializer = self.get_serializer(voting_proxy_request)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        voting_proxy_request = self.get_object()
        validated_data = self.clean()
        action = validated_data.get("action", None)
        voting_proxy = self.clean_voting_proxy(
            voting_proxy_id=request.data.get("votingProxy", None)
        )
        action(voting_proxy=voting_proxy, voting_proxy_request=voting_proxy_request)

        return Response(
            {
                "firstName": voting_proxy.first_name,
                "status": voting_proxy.status,
            }
        )


class VotingProxyCreateAPIView(CreateVoterAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = VotingProxy.objects.all()
    serializer_class = CreateVotingProxySerializer


class VotingProxyRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = VotingProxy.objects.all()
    serializer_class = VotingProxySerializer
    NON_PERSONAL_FIELDS = (
        "firstName",
        "status",
        "isAvailable",
    )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        is_own_voting_proxy = (
            self.request.user.is_authenticated
            and self.request.user.person is not None
            and instance.person == self.request.user.person
        )

        return Response(
            {
                key: value
                for key, value in data.items()
                if is_own_voting_proxy or key in self.NON_PERSONAL_FIELDS
            }
        )


class ReplyToVotingProxyRequestsAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = VotingProxy.objects.respectable()
    serializer_class = None

    def retrieve(self, request, *args, **kwargs):
        voting_proxy = self.get_object()
        voting_proxy_request_pks = []
        voting_proxy_requests = []
        is_read_only = request.GET.get("ro", "0") == "1"

        if request.GET.get("vpr", None):
            voting_proxy_request_pks = request.GET.get("vpr").split(",")

        try:
            voting_proxy_requests = get_voting_proxy_requests_for_proxy(
                voting_proxy, voting_proxy_request_pks
            )
        except VotingProxyRequest.DoesNotExist:
            is_read_only = True

        # Check if request exist that are already been accepted by the user
        if is_read_only:
            voting_proxy_requests = VotingProxyRequest.objects.upcoming().filter(
                proxy=voting_proxy
            )

        return Response(
            {
                "firstName": voting_proxy.first_name,
                "readOnly": is_read_only,
                "requests": [
                    {
                        "id": request.id,
                        "status": request.status,
                        "firstName": request.first_name,
                        "pollingStationNumber": request.polling_station_number,
                        "pollingStationLabel": request.polling_station_label,
                        "votingDate": dict(VotingProxyRequest.VOTING_DATE_CHOICES)[
                            request.voting_date
                        ],
                        "commune": request.commune.nom if request.commune else None,
                        "consulate": (
                            request.consulate.nom if request.consulate else None
                        ),
                    }
                    for request in voting_proxy_requests.order_by("voting_date")
                ],
            }
        )

    def clean(self):
        data = self.request.data
        voting_proxy = self.get_object()

        if data.get("action", None) == "accept":
            action = accept_voting_proxy_requests
        elif data.get("action", None) == "decline":
            action = mark_voting_proxy_as_unavailable
        else:
            raise ValidationError(
                detail={"action": "La valeur de ce champ n'est pas valide"}
            )

        if not data.get("votingProxyRequests", None):
            raise ValidationError(
                detail={
                    "votingProxyRequests": "La valeur de ce champ est obligatoire et devrait être une liste de uuids"
                }
            )

        try:
            voting_proxy_requests = get_voting_proxy_requests_for_proxy(
                voting_proxy, data.get("votingProxyRequests")
            )
        except (VotingProxyRequest.DoesNotExist, exceptions.ValidationError):
            raise ValidationError(
                detail={
                    "global": "Cette procuration a été acceptée par un·e autre volontaire. Nous vous enverrons un SMS "
                    "lorsqu'une nouvelle demande apparaîtra près de chez vous."
                }
            )

        return {
            "action": action,
            "voting_proxy": voting_proxy,
            "voting_proxy_requests": voting_proxy_requests,
        }

    def update(self, request, *args, **kwargs):
        validated_data = self.clean()
        action = validated_data.pop("action")
        action(**validated_data)

        return Response(
            {
                "firstName": validated_data["voting_proxy"].first_name,
                "status": validated_data["voting_proxy"].status,
            }
        )


class VotingProxyRequestsForProxyListAPIView(ListAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = VotingProxy.objects.respectable()
    serializer_class = None

    def serialize_data(self, voting_proxy, voting_proxy_requests):
        data = {
            "id": str(voting_proxy.id),
            "firstName": voting_proxy.first_name,
            "requests": [],
        }

        if not voting_proxy_requests:
            return data

        voting_proxy_requests = voting_proxy_requests[:20]
        voting_proxy_request_pks = sum(
            [request["ids"] for request in voting_proxy_requests], []
        )

        if not voting_proxy_request_pks:
            return data

        requests = {
            request.pk: request
            for request in VotingProxyRequest.objects.filter(
                pk__in=voting_proxy_request_pks
            )
        }

        for request in voting_proxy_requests:
            ids = request.get("ids")
            voting_dates = [d.strftime("%Y-%m-%d") for d in request.get("voting_dates")]
            first_request = requests.get(ids[0])
            request_data = {
                "ids": ids,
                "votingDates": voting_dates,
                "firstName": first_request.first_name,
                "pollingStationLabel": first_request.polling_station_label,
                "commune": first_request.commune.nom if first_request.commune else None,
                "consulate": (
                    first_request.consulate.nom if first_request.consulate else None
                ),
            }

            if len(ids) > 1:
                request_data["replyURL"] = front_url(
                    "reply_to_voting_proxy_requests",
                    kwargs={"pk": voting_proxy.pk},
                    query={"vpr": ",".join([str(pk) for pk in ids])},
                    absolute=False,
                )
            else:
                request_data["replyURL"] = front_url(
                    "reply_to_single_voting_proxy_request",
                    args=(first_request.pk,),
                    query={"vp": voting_proxy.pk},
                    absolute=False,
                )

            data["requests"].append(request_data)

        return data

    def list(self, request, *args, **kwargs):
        voting_proxy = self.get_object()
        voting_proxy_requests = get_acceptable_voting_proxy_requests_for_proxy(
            voting_proxy
        )
        data = self.serialize_data(voting_proxy, voting_proxy_requests)

        return Response(data)


class VotingProxyForRequestRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = VotingProxyRequest.objects.filter(proxy__isnull=False)
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
    permission_classes = (IsActionPopulaireClientPermission,)
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


class VotingProxyRequestCancelAPIView(VotingProxyRequestConfirmAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = VotingProxyRequest.objects.filter(proxy__isnull=False)

    def update(self, request, *args, **kwargs):
        voting_proxy_requests = self.get_voting_proxy_requests(request.data)
        cancel_voting_proxy_requests(voting_proxy_requests)
        return Response(status=status.HTTP_200_OK)


class VotingProxyRequestAcceptationCancelAPIView(VotingProxyRequestConfirmAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    queryset = VotingProxyRequest.objects.filter(proxy__isnull=False)

    def update(self, request, *args, **kwargs):
        voting_proxy_requests = self.get_voting_proxy_requests(request.data)
        cancel_voting_proxy_request_acceptation(voting_proxy_requests)
        return Response(status=status.HTTP_200_OK)


class AcceptedVotingProxyRequestListAPIView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = VotingProxyRequest.objects.upcoming().filter(
        status__in=(
            VotingProxyRequest.STATUS_ACCEPTED,
            VotingProxyRequest.STATUS_CONFIRMED,
            VotingProxyRequest.STATUS_CANCELLED,
        ),
    )
    serializer_class = AcceptedVotingProxyRequestSerializer

    def get_queryset(self):
        pks = self.request.GET.get("vpr", None)
        if not pks:
            raise Http404
        pks = pks.split(",")
        queryset = self.queryset.filter(pk__in=pks)
        if not queryset.exists():
            raise Http404
        email = queryset.first().email
        return self.queryset.filter(email=email).order_by("voting_date")
