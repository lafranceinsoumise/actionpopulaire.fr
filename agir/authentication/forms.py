from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Row, Div, Layout
from django import forms
from django.contrib.auth import authenticate

from agir.authentication.tokens import short_code_generator
from agir.lib.token_bucket import TokenBucket
from agir.people.models import Person
from .tasks import send_login_email, send_no_account_email

send_mail_email_bucket = TokenBucket("SendMail", 5, 600)
send_mail_ip_bucket = TokenBucket("SendMailIP", 5, 600)
check_short_code_bucket = TokenBucket("CheckShortCode", 5, 180)


class EmailForm(forms.Form):
    messages = {
        "unknown": "Cette adresse email ne correspond pas à un signataire.",
        "rate_limited": "Vous avez déjà demandé plusieurs emails de connexion. Veuillez laisser quelques minutes pour"
        " vérifier la bonne réception avant d'en demander d'autres.",
    }

    email = forms.EmailField(required=True)

    def __init__(self, has_bookmarked_emails=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].label = ""
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Se connecter"))

    def clean_email(self):
        # normalisation des emails
        return self.cleaned_data["email"].lower()

    def send_email(self, request_ip):
        email = self.cleaned_data["email"]

        # on contrôle sur l'email ET sur l'IP
        if not send_mail_email_bucket.has_tokens(
            email.lower()
        ) or not send_mail_ip_bucket.has_tokens(request_ip):
            self.add_error(
                "email",
                forms.ValidationError(self.messages["rate_limited"], "rate_limited"),
            )
            return False

        # On génère un short_code que la personne existe ou pas, pour éviter les timings attacks
        self.short_code, self.expiration = short_code_generator.generate_short_code(
            email
        )

        try:
            self.person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            self.person = None
            send_no_account_email.delay(email)
        else:
            send_login_email.apply_async(
                args=(
                    self.cleaned_data["email"],
                    self.short_code,
                    self.expiration.timestamp(),
                ),
                expires=10 * 60,
            )

        return True


class CodeForm(forms.Form):
    messages = {
        "incorrect_format": "Le code que vous avez entré n'est pas au bon format. Il est constitué de 5 lettres ou"
        " chiffres et se trouve dans l'email qui vous a été envoyé.",
        "wrong_code": "Le code que vous avez entré n'est pas ou plus valide. Vérifiez que vous l'avez saisi"
        " correctement, et qu'il est bien valide, comme indiqué dans l'email reçu.",
        "rate_limited": "Vous avez fait plusieurs tentatives de connexions erronées d'affilée. Merci de patienter un"
        " peu avant de retenter.",
    }

    code = forms.CharField(label="Code de connexion", max_length=8)

    def __init__(self, *args, email, **kwargs):
        super().__init__(*args, **kwargs)

        self.email = email
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Valider"))

    def clean_code(self):
        code = self.cleaned_data["code"].replace(" ", "")

        if not short_code_generator.is_allowed_pattern(code):
            raise forms.ValidationError(
                self.messages["incorrect_format"], "incorrect_format"
            )

        if not check_short_code_bucket.has_tokens(self.email):
            raise forms.ValidationError(self.messages["rate_limited"], "rate_limited")

        self.role = authenticate(email=self.email, short_code=code)
        if self.role:
            return code

        raise forms.ValidationError(self.messages["wrong_code"], "wrong_code")
