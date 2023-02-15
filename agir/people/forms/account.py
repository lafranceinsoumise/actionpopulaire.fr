import logging
from datetime import timedelta

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Row, Submit, Layout, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form, CharField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from agir.lib.form_components import HalfCol
from agir.lib.phone_numbers import (
    normalize_overseas_numbers,
    is_french_number,
    is_mobile_number,
)
from agir.people.actions.validation_codes import (
    send_new_code,
    RateLimitedException,
    is_valid_code,
)
from agir.people.models import Person, PersonEmail, PersonValidationSMS
from agir.people.tasks import send_confirmation_change_email
from agir.people.token_buckets import ChangeMailBucket

logger = logging.getLogger(__name__)


class PreferencesFormMixin(forms.ModelForm):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.layout = Layout(*self.get_fields())

    def get_fields(self, fields=None):
        fields = fields or []

        return fields

    def _save_m2m(self):
        """Reorder addresses so that the selected one is number one"""
        super()._save_m2m()
        if "primary_email" in self.cleaned_data:
            self.instance.set_primary_email(self.cleaned_data["primary_email"])

    class Meta:
        model = Person
        fields = ["contact_phone"]


class AddEmailForm(forms.ModelForm):
    def __init__(self, person, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance.person = person
        self.fields["address"].label = _("Nouvelle adresse")
        self.fields["address"].help_text = _(
            "Utiliser ce champ pour ajouter une adresse supplémentaire que vous pouvez"
            " utiliser pour vous connecter."
        )
        self.fields["address"].error_messages.update(
            {
                "unique": "Cette adresse est déjà rattaché à un autre compte.",
                "rate_limit": "Trop d'email de confirmation envoyés. Merci de réessayer dans quelques minutes.",
            }
        )
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Ajouter"))

    def send_confirmation(self, user_pk):
        new_mail = self.cleaned_data["address"]
        if not ChangeMailBucket.has_tokens(user_pk):
            self.add_error(
                "address", self.fields["address"].error_messages["rate_limit"]
            )
            return None

        send_confirmation_change_email.delay(new_email=new_mail, user_pk=str(user_pk))
        return new_mail

    class Meta:
        model = PersonEmail
        fields = ("address",)


class SendValidationSMSForm(forms.ModelForm):
    error_messages = {
        "french_only": "Pour des raisons techniques, l'opération ne peut être réalisée qu'avec des numéros français. "
        "Pas d'inquiétude si vous n'avez pas de numéro français, elle n'est pas obligatoire !",
        "mobile_only": "Vous devez donner un numéro de téléphone mobile.",
        "rate_limited": "Trop de SMS envoyés. Merci de réessayer dans quelques minutes.",
        "already_used": "Ce numéro a déjà été utilisé pour voter. Si vous le partagez avec une autre"
        ' personne, <a href="{}">vous pouvez'
        " exceptionnellement en demander le déblocage</a>.",
    }

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

        if (
            not self.is_bound
            and self.instance.contact_phone
            and not (
                is_french_number(self.instance.contact_phone)
                and is_mobile_number(self.instance.contact_phone)
            )
        ):
            self.initial["contact_phone"] = ""
            self.fields["contact_phone"].help_text = _(
                "Seul un numéro de téléphone mobile français (outremer inclus) peut être utilisé pour la validation."
            )

        self.fields["contact_phone"].required = True
        self.fields["contact_phone"].error_messages["required"] = _(
            "Vous devez indiquer le numéro de mobile qui vous servira à valider votre compte."
        )

        phone_input = Field("contact_phone")
        submit_button = Submit("submit", "Recevoir mon code")

        fields = [Row(HalfCol(phone_input, submit_button))]
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.layout = Layout(*fields)

    def clean_contact_phone(self):
        phone_number = normalize_overseas_numbers(self.cleaned_data["contact_phone"])

        if not is_french_number(phone_number):
            raise ValidationError(self.error_messages["french_only"], "french_only")

        if not is_mobile_number(phone_number):
            raise ValidationError(self.error_messages["mobile_only"], "mobile_only")

        return phone_number

    def send_code(self, request):
        try:
            return send_new_code(self.instance, request=request)
        except RateLimitedException:
            self.add_error(
                "contact_phone",
                ValidationError(self.error_messages["rate_limited"], "rate_limited"),
            )
            return None

    class Meta:
        model = Person
        fields = ("contact_phone",)


class CodeValidationForm(Form):
    code = CharField(label=_("Code reçu par SMS"))

    def __init__(self, *args, person, **kwargs):
        super().__init__(*args, **kwargs)
        self.person = person

        phone_input = Field("code")
        submit_button = Submit("submit", "Valider mon numéro")

        fields = [Row(HalfCol(phone_input, submit_button))]

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.layout = Layout(*fields)

    def clean_code(self):
        # remove spaces added by Cleave.js
        code = self.cleaned_data["code"].replace(" ", "")

        try:
            if is_valid_code(self.person, code):
                return code
        except RateLimitedException:
            raise ValidationError(
                "Trop de tentative échouées. Veuillez patienter une minute par mesure de sécurité."
            )

        codes = [
            code["code"]
            for code in PersonValidationSMS.objects.values("code").filter(
                person=self.person, created__gt=timezone.now() - timedelta(minutes=30)
            )
        ]
        logger.warning(
            f"{self.person.display_email} SMS code failure : tried {self.cleaned_data['code']} and valid"
            f" codes were {', '.join(codes)}"
        )

        if len(code) == 5:
            raise ValidationError(
                "Votre code est incorrect. Attention : le code demandé figure "
                "dans le SMS et comporte 6 chiffres. Ne le confondez pas avec le numéro court "
                "de l'expéditeur (5 chiffres)."
            )

        raise ValidationError("Votre code est incorrect ou expiré.")


class MembreReseauElusForm(forms.ModelForm):
    membre_reseau_elus = forms.ChoiceField(
        label="Souhaitez-vous etre membre du réseau des élu⋅es insoumis⋅es et citoyen⋅nes ?",
        required=True,
        choices=(
            (
                Person.MEMBRE_RESEAU_SOUHAITE,
                "Je souhaite rejoindre le réseau des élu⋅es",
            ),
            (
                Person.MEMBRE_RESEAU_NON,
                "Je ne souhaite pas rejoindre le réseau des élu⋅es",
            ),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        status = self.instance.membre_reseau_elus
        self.helper.layout = Layout("membre_reseau_elus")

        if status == Person.MEMBRE_RESEAU_INCONNU:
            self.helper.add_input(Submit("valider", "Valider"))
        elif status in [Person.MEMBRE_RESEAU_SOUHAITE, Person.MEMBRE_RESEAU_OUI]:
            self.fields["membre_reseau_elus"].widget = forms.HiddenInput()
            self.fields["membre_reseau_elus"].choices = (
                (Person.MEMBRE_RESEAU_NON, ""),
            )
            self.initial["membre_reseau_elus"] = Person.MEMBRE_RESEAU_NON
            self.helper.layout.fields.append(
                HTML(
                    "Vous ne souhaitez plus faire partie du réseau des élu⋅es ? Signalez-le ici."
                ),
            )
            self.helper.add_input(
                Submit(
                    "valider",
                    "Je ne souhaite plus faire partie du réseau des élu⋅es",
                    css_class="margintopmore btn-wrap",
                )
            )
        elif status == Person.MEMBRE_RESEAU_NON:
            self.fields["membre_reseau_elus"].widget = forms.HiddenInput()
            self.fields["membre_reseau_elus"].choices = (
                (Person.MEMBRE_RESEAU_SOUHAITE, ""),
            )
            self.initial["membre_reseau_elus"] = Person.MEMBRE_RESEAU_SOUHAITE
            self.helper.layout.fields.append(
                HTML(
                    "Vous souhaitez finalement faire partie du réseau des élu⋅s ? Signalez le-nous."
                ),
            )
            self.helper.add_input(
                Submit("valider", "Je souhaite faire partie du réseau des élu⋅es")
            )

    class Meta:
        model = Person
        fields = ("membre_reseau_elus",)
