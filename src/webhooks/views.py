import json
import base64

import requests
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import BasePermission
from rest_framework import exceptions

from people.models import Person
from people.serializers import LegacyPersonSerializer
from api import settings


class NbAddPeopleView(APIView):
    """Add people to the API when they register on NationBuilder"""

    permission_classes = ()

    def post(self, request):
        if (request.data['token'] != settings.NB_WEBHOOK_KEY):
            return Response('Wrong token', 401)
        nb_person = request.data['payload']['person']
        nb_person_serializer = LegacyPersonSerializer(data=nb_person)
        if not nb_person_serializer.is_valid():
            return Response('Invalid payload', 400)
        nb_person_serializer.save()
        return Response({'status': 'Accepted'}, 202)


class SendgridSesWebhookAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password):
        if userid != settings.SENDGRID_SES_WEBHOOK_USER or password != settings.SENDGRID_SES_WEBHOOK_PASSWORD:
            raise exceptions.AuthenticationFailed('Invalid username/password.')

        return (userid, None)


class IsBasicAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user == settings.SENDGRID_SES_WEBHOOK_USER


class BounceView(APIView):
    permission_classes = (IsBasicAuthenticated,)
    authentication_classes = (SendgridSesWebhookAuthentication,)

    def handleBounce(self, recipient_email):
        try:
            person = Person.objects.get(email=recipient_email)
        except Person.DoesNotExist:
            return

        if (person.created + timezone.timedelta(hours=1) < timezone.now()):
            person.bounced = True
            person.save()
            return

        if person.nb_id is not None:
            requests.delete('https://plp.nationbuilder.com/api/v1/people/' + str(person.nb_id),
            params={'access_token': settings.NB_API_KEY})
        person.delete()


class WrongContentTypeJSONParser(JSONParser):
    media_type = 'text/plain'


class SesBounceView(BounceView):
    parser_classes = (WrongContentTypeJSONParser,)

    def post(self, request):
        response = Response({'status': 'Accepted'}, 202)
        if (request.data['Type'] == 'SubscriptionConfirmation'):
            requests.get(request.data['SubscribeURL'])
            return response
        if (request.data['Type'] != 'Notification'):
            return response

        message = json.loads(request.data['Message'])
        if (message['notificationType'] != 'Bounce'):
            return response
        if (message['bounce']['bounceType'] != 'Permanent'):
            return response

        self.handleBounce(message['mail']['destination'][0])

        return response


class SendgridBounceView(BounceView):
    def post(self, request):
        for webhook in request.data:
            if webhook['event'] != 'bounce':
                continue
            self.handleBounce(webhook['email'])
        return Response({'status': 'Accepted'}, 202)
