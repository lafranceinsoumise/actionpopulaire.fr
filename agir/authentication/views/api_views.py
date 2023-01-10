from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from rest_framework import exceptions, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from agir.authentication.serializers import SessionSerializer, SessionDonationSerializer
from agir.authentication.tasks import send_login_email, send_no_account_email
from agir.authentication.tokens import short_code_generator
from agir.lib.rest_framework_permissions import IsActionPopulaireClientPermission
from agir.lib.token_bucket import TokenBucket
from agir.lib.utils import get_client_ip
from agir.people.models import Person, PersonEmail

__all__ = [
    "CSRFAPIView",
    "SessionContextAPIView",
    "SessionDonationAPIView",
    "LoginAPIView",
    "CheckCodeAPIView",
    "LogoutAPIView",
    "ping",
]

send_mail_email_bucket = TokenBucket("SendMail", 5, 600)
send_mail_ip_bucket = TokenBucket("SendMailIP", 5, 120)
check_short_code_bucket = TokenBucket("CheckShortCode", 5, 180)


class CSRFAPIView(APIView):
    permission_classes = (IsActionPopulaireClientPermission,)

    def get(self, request, *args, **kwargs):
        return Response({"csrfToken": get_token(request)})


class SessionContextAPIView(RetrieveAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    serializer_class = SessionSerializer
    queryset = None

    def initial(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            request.session.modified = True  # force updating of cookie expiration
        return super().initial(request, *args, **kwargs)

    def get_object(self):
        return self.request


# Retrieve specific session filled with Donation informations
class SessionDonationAPIView(RetrieveAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    serializer_class = SessionDonationSerializer
    queryset = None

    def get_object(self):
        return self.request


@never_cache
@api_view(["HEAD"])
@permission_classes((permissions.AllowAny,))
def ping(request):
    return Response()


class LoginAPIView(APIView):
    permission_classes = (IsActionPopulaireClientPermission,)
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

        if settings.DEBUG:
            return

        client_ip = get_client_ip(self.request)

        if not send_mail_email_bucket.has_tokens(
            email
        ) or not send_mail_ip_bucket.has_tokens(client_ip):
            raise exceptions.Throttled(
                detail=self.messages["throttled"], code="throttled"
            )

    def send_authentication_email(self, email):
        self.request.session["login_email"] = email
        short_code = None
        expiration = None
        try:
            Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            send_no_account_email.delay(email)
        else:
            short_code, expiration = short_code_generator.generate_short_code(email)
            send_login_email.apply_async(
                args=(
                    email,
                    short_code,
                    expiration.timestamp(),
                ),
                expires=10 * 60,
            )
        return short_code, expiration

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "").lower()
        self.validate(email)
        short_code, expiration = self.send_authentication_email(email)
        if settings.DEBUG:
            return Response(
                status=status.HTTP_200_OK,
                data={"code": short_code, "expiration": expiration},
            )
        return Response(status=status.HTTP_200_OK)


class CheckCodeAPIView(APIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    messages = {
        "invalid_format": "Le code que vous avez entré n'est pas au bon format. Il est constitué de 5 lettres ou"
        " chiffres et se trouve dans l'email qui vous a été envoyé.",
        "invalid_code": "Le code que vous avez entré n'est pas ou plus valide. Vérifiez qu'il s'agit bien du code "
        "que vous avez reçu à l'instant, et pas d'un ancien code.",
        "throttled": "Vous avez fait plusieurs tentatives de connexions erronées d'affilée. Merci de patienter un"
        " peu avant de retenter.",
    }

    def validate(self, email, code):
        if not short_code_generator.is_allowed_pattern(code):
            raise exceptions.ValidationError(
                detail={"code": self.messages["invalid_format"]}, code="invalid_format"
            )

        if not settings.DEBUG and not check_short_code_bucket.has_tokens(email):
            raise exceptions.Throttled(
                detail=self.messages["throttled"], code="throttled"
            )

        role = authenticate(email=email, short_code=code)

        if not role:
            raise exceptions.ValidationError(
                detail={"code": self.messages["invalid_code"]}, code="invalid_code"
            )

        return role

    def do_login(self, email, role):
        login(self.request, role)

        try:
            validated_email_instance = role.person.emails.get_by_natural_key(email)
        except PersonEmail.DoesNotExist:
            # en cas de connexion pile au moment de la suppression d'une adresse email...
            pass
        else:
            if validated_email_instance.bounced:
                validated_email_instance.bounced = False
                validated_email_instance.bounced_date = None
                validated_email_instance.save()

            if (
                validated_email_instance != role.person.primary_email
                and role.person.primary_email.bounced
            ):
                role.person.set_primary_email(validated_email_instance)

    def post(self, request, *args, **kwargs):
        email = request.session.get("login_email")
        if not email:
            raise exceptions.MethodNotAllowed(method="post", code="method_not_allowed")
        code = request.data.get("code", "").replace(" ", "").upper()
        role = self.validate(email, code)
        last_login = role.last_login
        self.do_login(email, role)
        return Response(
            status=status.HTTP_200_OK,
            data={
                "lastLogin": last_login,
            },
        )


class LogoutAPIView(APIView):
    permission_classes = (IsActionPopulaireClientPermission,)

    def get(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)
