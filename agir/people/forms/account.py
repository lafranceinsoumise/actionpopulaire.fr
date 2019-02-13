from datetime import timedelta

import logging
from crispy_forms.bootstrap import FormActions, FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Row, Div, Submit, Layout
from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form, CharField
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from agir.lib.form_components import HalfCol
from agir.lib.form_mixins import TagMixin
from agir.lib.phone_numbers import (
    normalize_overseas_numbers,
    is_french_number,
    is_mobile_number,
)

from agir.people.actions.validation_codes import (
    send_new_code,
    RateLimitedException,
    ValidationCodeSendingException,
    is_valid_code,
)
from agir.people.models import PersonTag, Person, PersonEmail, PersonValidationSMS
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
        emails = self.instance.emails.all()
        self.several_mails = len(emails) > 1

        fields = fields or []

        block_template = """
                    <label class="control-label">{label}</label>
                    <div class="controls">
                      <div>{value}</div>
                      <p class="help-block">{help_text}</p>
                    </div>
                """

        email_management_block = HTML(
            format_html(
                block_template,
                label=_("Gérez vos adresses emails"),
                value=format_html(
                    '<a href="{}" class="btn btn-default">{}</a>',
                    reverse("email_management"),
                    _("Accéder au formulaire de gestion de vos emails"),
                ),
                help_text=_(
                    "Ce formulaire vous permet d'ajouter de nouvelles adresses ou de supprimer les existantes"
                ),
            )
        )

        validation_link = format_html(
            '<input type="submit" name="validation" value="{label}" class="btn btn-default">',
            label=_("Valider mon numéro de téléphone"),
        )

        unverified = (
            self.instance.contact_phone_status == Person.CONTACT_PHONE_UNVERIFIED
        )

        validation_block = HTML(
            format_html(
                block_template,
                label=_("Vérification de votre compte"),
                value=validation_link
                if unverified
                else f"Compte {self.instance.get_contact_phone_status_display().lower()}",
                help_text=_(
                    "Validez votre numéro de téléphone afin de certifier votre compte"
                )
                if unverified
                else "",
            )
        )

        email_fieldset_name = _("Mes adresses emails")
        email_label = _("Email de contact")
        email_help_text = _(
            "L'adresse que nous utilisons pour vous envoyer les lettres d'informations et les notifications."
        )

        if self.several_mails:
            self.fields["primary_email"] = forms.ModelChoiceField(
                queryset=emails,
                required=True,
                label=email_label,
                initial=emails[0],
                help_text=email_help_text,
            )
            fields.append(
                Fieldset(
                    email_fieldset_name,
                    Row(HalfCol("primary_email"), HalfCol(email_management_block)),
                )
            )
        else:
            fields.append(
                Fieldset(
                    email_fieldset_name,
                    Row(
                        HalfCol(
                            HTML(
                                block_template.format(
                                    label=email_label,
                                    value=emails[0].address,
                                    help_text=email_help_text,
                                )
                            )
                        ),
                        HalfCol(email_management_block),
                    ),
                )
            )

        fields.append(
            Fieldset(
                _("Mon numéro de téléphone"),
                Row(HalfCol("contact_phone"), HalfCol(validation_block)),
            )
        )

        return fields

    def _save_m2m(self):
        """Reorder addresses so that the selected one is number one"""
        super()._save_m2m()
        if "primary_email" in self.cleaned_data:
            self.instance.set_primary_email(self.cleaned_data["primary_email"])

    class Meta:
        model = Person
        fields = ["contact_phone"]


class ExternalPersonPreferencesForm(PreferencesFormMixin):
    is_insoumise = forms.BooleanField(
        required=False,
        label=_("Je souhaite rejoindre la France insoumise"),
        help_text=_(
            "Cette action transformera votre compte de manière à vous permettre d'utiliser"
            " toutes les fonctionnalités de la plateforme. Vous recevrez les lettres d'information, et vous pourrez "
            "participer à la vie du mouvement."
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["is_insoumise"]:
            cleaned_data["subscribed"] = True
            cleaned_data["group_notifications"] = True
            cleaned_data["event_notifications"] = True

    def get_fields(self, fields=None):
        fields = super().get_fields()
        fields.append(FormActions(Submit("submit", "Sauvegarder mes préférences")))
        fields.extend(
            [
                Fieldset(
                    _("Rejoindre la France insoumise"),
                    "is_insoumise",
                    FormActions(Submit("submit", "Valider")),
                )
            ]
        )

        return fields

    class Meta(PreferencesFormMixin.Meta):
        fields = ["contact_phone", "is_insoumise"]


class InsoumisePreferencesForm(TagMixin, PreferencesFormMixin):
    tags = [
        (
            "newsletter_efi",
            _(
                "Recevoir les informations liées aux cours de l'École de Formation insoumise"
            ),
        )
    ]
    tag_model_class = PersonTag

    def get_fields(self, fields=None):
        fields = super().get_fields()
        fields.extend(
            [
                Fieldset(
                    _("Préférences d'emails"),
                    "subscribed",
                    Div("newsletter_efi", style="margin-left: 50px;"),
                    "group_notifications",
                    "event_notifications",
                ),
                FormActions(
                    Submit(
                        "no_mail",
                        "Ne plus recevoir d'emails du tout",
                        css_class="btn-danger",
                    ),
                    css_class="text-right",
                ),
                Fieldset(
                    _("Ma participation"),
                    Row(HalfCol("draw_participation"), HalfCol("gender")),
                ),
            ]
        )

        fields.append(FormActions(Submit("submit", "Sauvegarder mes préférences")))

        return fields

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

        self.no_mail = data is not None and "no_mail" in data

        self.fields["gender"].help_text = _(
            "La participation aux tirages au sort étant paritaire, merci d'indiquer"
            " votre genre si vous souhaitez être tirés au sort."
        )
        self.fields["newsletter_efi"].help_text = _(
            "Je recevrai notamment des infos et des rappels sur les cours " "à venir."
        )

    def clean(self):
        cleaned_data = super().clean()

        if self.no_mail:
            # if the user clicked the "unsubscribe from all button", we want to put all fields thare are boolean
            # to false, and keep all the others to their initial values: it allows posting to this form with
            # the single "no_mail" content
            for k, v in cleaned_data.items():
                if isinstance(v, bool):
                    cleaned_data[k] = False
                else:
                    cleaned_data[k] = self.get_initial_for_field(self.fields[k], k)

        if cleaned_data["draw_participation"] and not cleaned_data["gender"]:
            self.add_error(
                "gender",
                forms.ValidationError(
                    _(
                        "Votre genre est obligatoire pour pouvoir organiser un tirage au sort paritaire"
                    )
                ),
            )

        return cleaned_data

    class Meta(PreferencesFormMixin.Meta):
        fields = [
            "subscribed",
            "group_notifications",
            "event_notifications",
            "draw_participation",
            "gender",
            "contact_phone",
        ]


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
        "french_only": "Le numéro doit être un numéro de téléphone français.",
        "mobile_only": "Vous devez donner un numéro de téléphone mobile.",
        "rate_limited": "Trop de SMS envoyés. Merci de réessayer dans quelques minutes.",
        "sending_error": "Le SMS n'a pu être envoyé suite à un problème technique. Merci de réessayer plus tard.",
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

        fields = [
            Row(
                HalfCol(
                    FieldWithButtons(
                        "contact_phone", Submit("submit", "Recevoir mon code")
                    )
                )
            )
        ]
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
        except ValidationCodeSendingException:
            self.add_error(
                "contact_phone",
                ValidationError(self.error_messages["sending_error"], "sending_error"),
            )

    class Meta:
        model = Person
        fields = ("contact_phone",)


class CodeValidationForm(Form):
    code = CharField(label=_("Code reçu par SMS"))

    def __init__(self, *args, person, **kwargs):
        super().__init__(*args, **kwargs)
        self.person = person

        fields = [
            Row(
                HalfCol(
                    FieldWithButtons("code", Submit("submit", "Valider mon numéro"))
                )
            )
        ]
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
            f"{self.person.email} SMS code failure : tried {self.cleaned_data['code']} and valid"
            f" codes were {', '.join(codes)}"
        )

        if len(code) == 5:
            raise ValidationError(
                "Votre code est incorrect. Attention : le code demandé figure "
                "dans le SMS et comporte 6 chiffres. Ne le confondez pas avec le numéro court "
                "de l'expéditeur (5 chiffres)."
            )

        raise ValidationError("Votre code est incorrect ou expiré.")
