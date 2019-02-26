from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth import authenticate

from agir.authentication.crypto import short_code_generator
from agir.lib.token_bucket import TokenBucket
from agir.people.models import Person
from .tasks import send_login_email

send_mail_bucket = TokenBucket("SendMail", 5, 600)
check_short_code_bucket = TokenBucket("CheckShortCode", 5, 180)


class EmailForm(forms.Form):
    messages = {
        "unknown": "Cette adresse email ne correspond pas à un signataire.",
        "rate_limited": "Vous avez déjà demandé plusieurs emails de connexion. Veuillez laisser quelques minutes pour"
        " vérifier la bonne réception avant d'en demander d'autres.",
    }

    email = forms.EmailField(label="Votre adresse email", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Valider"))

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            self.person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            raise forms.ValidationError(self.messages["unknown"], "unknown")

        return email

    def send_email(self):
        if not send_mail_bucket.has_tokens(self.person.pk):
            self.add_error(
                "email",
                forms.ValidationError(self.messages["rate_limited"], "rate_limited"),
            )
            return False

        self.short_code, self.expiration = short_code_generator.generate_short_code(
            self.person.pk, meta={"email": self.cleaned_data["email"]}
        )
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

    def __init__(self, *args, person, **kwargs):
        self.person = person
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Valider"))

    def clean_code(self):
        code = self.cleaned_data["code"].replace(" ", "")

        if not short_code_generator.is_allowed_pattern(code):
            raise forms.ValidationError(
                self.messages["incorrect_format"], "incorrect_format"
            )

        if not check_short_code_bucket.has_tokens(self.person.pk):
            raise forms.ValidationError(self.messages["rate_limited"], "rate_limited")

        self.role = authenticate(user_pk=self.person.pk, short_code=code)
        if self.role:
            return code

        raise forms.ValidationError(self.messages["wrong_code"], "wrong_code")
