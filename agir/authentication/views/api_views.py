from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from rest_framework import exceptions, permissions, status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response

from agir.authentication.serializers import SessionSerializer
from agir.authentication.tasks import send_login_email, send_no_account_email
from agir.authentication.tokens import short_code_generator
from agir.lib.token_bucket import TokenBucket
from agir.lib.utils import get_client_ip
from agir.people.models import Person

__all__ = [
    "SessionContextAPIView",
    "LoginAPIView",
]

send_mail_email_bucket = TokenBucket("SendMail", 5, 600)
send_mail_ip_bucket = TokenBucket("SendMailIP", 5, 600)


class SessionContextAPIView(RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SessionSerializer
    queryset = None

    def get_object(self):
        return self.request


class LoginAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Person.objects.all()
    messages = {
        "invalid_format": "Saisissez une adresse e-mail valide.",
        "throttled": "Vous avez déjà demandé plusieurs emails de connexion. Veuillez laisser quelques minutes pour"
        " vérifier la bonne réception avant d'en demander d'autres.",
    }

    def validate(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise exceptions.ValidationError(
                detail={"email": self.messages["invalid_format"]}, code="invalid_format"
            )

        client_ip = get_client_ip(self.request)
        if not send_mail_email_bucket.has_tokens(
            email
        ) or not send_mail_ip_bucket.has_tokens(client_ip):
            raise exceptions.Throttled(
                detail=self.messages["throttled"], code="throttled"
            )

    def send_authentication_email(self, email):
        self.request.session["login_email"] = email
        try:
            Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            send_no_account_email.delay(email)
        else:
            short_code, expiration = short_code_generator.generate_short_code(email)
            send_login_email.apply_async(
                args=(email, short_code, expiration.timestamp(),), expires=10 * 60,
            )

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "").lower()
        self.validate(email)
        self.send_authentication_email(email)
        return Response(status=status.HTTP_200_OK)
