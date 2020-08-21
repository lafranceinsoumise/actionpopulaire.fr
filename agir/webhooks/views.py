import json
import logging

import requests
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import BasePermission
from rest_framework import exceptions

from agir.people.models import PersonEmail
from django.conf import settings


logger = logging.getLogger(__name__)


class SendgridSesWebhookAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        if (
            userid != settings.SENDGRID_SES_WEBHOOK_USER
            or password != settings.SENDGRID_SES_WEBHOOK_PASSWORD
        ):
            raise exceptions.AuthenticationFailed("Invalid username/password.")

        return (userid, None)


class IsBasicAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user == settings.SENDGRID_SES_WEBHOOK_USER


class BounceView(APIView):
    permission_classes = (IsBasicAuthenticated,)
    authentication_classes = (SendgridSesWebhookAuthentication,)

    def handleBounce(self, recipient_email):
        # Auparavant on supprimait les personnes dont l'adresse email bounçait
        # dans l'heure suivant la création.
        pass


class WrongContentTypeJSONParser(JSONParser):
    media_type = "text/plain"


class SesBounceView(BounceView):
    parser_classes = (WrongContentTypeJSONParser,)

    def post(self, request):
        response = Response({"status": "Accepted"}, 202)
        if request.data["Type"] == "SubscriptionConfirmation":
            requests.get(request.data["SubscribeURL"])
            return response
        if request.data["Type"] != "Notification":
            return response

        message = json.loads(request.data["Message"])
        if message["notificationType"] != "Bounce":
            return response

        logger.info(f"Amazon Bounce: {json.dumps(message)}")

        if message["bounce"]["bounceType"] != "Permanent":
            return response

        self.handleBounce(message["mail"]["destination"][0])

        return response


class SendgridBounceView(BounceView):
    def post(self, request):
        for webhook in request.data:
            if webhook["event"] != "bounce" and webhook["event"] != "dropped":
                continue
            self.handleBounce(webhook["email"])
        return Response({"status": "Accepted"}, 202)
