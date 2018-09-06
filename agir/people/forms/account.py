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
from agir.lib.sms import normalize_mobile_phone, send_new_code, RateLimitedException, SMSSendException, is_valid_code
from agir.people.models import PersonTag, Person, PersonEmail, PersonValidationSMS

logger = logging.getLogger(__name__)

class MessagePreferencesForm(TagMixin, forms.ModelForm):
    tags = [('newsletter_efi', _("Recevoir les informations liées aux cours de l'École de Formation insoumise"))]
    tag_model_class = PersonTag

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

        self.no_mail = data is not None and 'no_mail' in data

        self.fields['gender'].help_text = _("La participation aux tirages au sort étant paritaire, merci d'indiquer"
                                            " votre genre si vous souhaitez être tirés au sort.")
        self.fields['newsletter_efi'].help_text = _('Je recevrai notamment des infos et des rappels sur les cours '
                                                    'à venir.')

        emails = self.instance.emails.all()
        self.several_mails = len(emails) > 1

        fields = []

        block_template = """
            <label class="control-label">{label}</label>
            <div class="controls">
              <div>{value}</div>
              <p class="help-block">{help_text}</p>
            </div>
        """

        email_management_block = HTML(block_template.format(
            label=_("Gérez vos adresses emails"),
            value=format_html(
                '<a href="{}" class="btn btn-default">{}</a>',
                reverse('email_management'),
                _("Accéder au formulaire de gestion de vos emails"),
            ),
            help_text=_("Ce formulaire vous permet d'ajouter de nouvelles adresses ou de supprimer les existantes"),
        ))

        validation_link = format_html(
            '<a href="{}" class="btn btn-default">{}</a>',
            reverse('send_validation_sms'),
            _("Valider mon numéro de téléphone"),
        )

        verified = self.instance.contact_phone_status == Person.CONTACT_PHONE_UNVERIFIED
        validation_block = HTML(block_template.format(
            label=_("Vérification de votre compte"),
            value=validation_link if verified else f"Compte {self.instance.get_contact_phone_status_display().lower()}",
            help_text=_("Validez votre numéro de téléphone afin de certifier votre compte") if verified else "",
        ))

        email_fieldset_name = _("Mes adresses emails")
        email_label = _("Email de contact")
        email_help_text = _(
            "L'adresse que nous utilisons pour vous envoyer les lettres d'informations et les notifications."
        )

        if self.several_mails:
            self.fields['primary_email'] = forms.ModelChoiceField(
                queryset=emails,
                required=True,
                label=email_label,
                initial=emails[0],
                help_text=email_help_text,
            )
            fields.append(
                Fieldset(
                    email_fieldset_name,
                    Row(
                        HalfCol('primary_email'),
                        HalfCol(email_management_block)
                    )
                )
            )
        else:
            fields.append(Fieldset(
                email_fieldset_name,
                Row(
                    HalfCol(
                        HTML(block_template.format(
                            label=email_label,
                            value=emails[0].address,
                            help_text=email_help_text
                        ))
                    ),
                    HalfCol(email_management_block)
                )
            ))

        fields.extend([
            Fieldset(
                _("Mon numéro de téléphone"),
                Row(
                    HalfCol('contact_phone'),
                    HalfCol(validation_block)
                )
            ),
            Fieldset(
                _("Préférences d'emails"),
                'subscribed',
                Div(
                    'newsletter_efi',
                    style='margin-left: 50px;'
                ),
                'group_notifications',
                'event_notifications',
            ),
            Fieldset(
                _("Ma participation"),
                Row(
                    HalfCol('draw_participation'),
                    HalfCol('gender'),
                )
            ),
            FormActions(
                Submit('submit', 'Sauvegarder mes préférences'),
                Submit('no_mail', 'Ne plus recevoir de mails du tout', css_class='btn-danger')
            )
        ])

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(*fields)

    def clean(self):
        cleaned_data = super().clean()

        if self.no_mail:
            for k, v in cleaned_data.items():
                if not isinstance(v, bool): continue
                cleaned_data[k] = False

        if cleaned_data['draw_participation'] and not cleaned_data['gender']:
            self.add_error(
                'gender',
                forms.ValidationError(
                    _("Votre genre est obligatoire pour pouvoir organiser un tirage au sort paritaire"))
            )

        return cleaned_data

    def _save_m2m(self):
        """Reorder addresses so that the selected one is number one"""
        super()._save_m2m()
        if 'primary_email' in self.cleaned_data:
            self.instance.set_primary_email(self.cleaned_data['primary_email'])

    class Meta:
        model = Person
        fields = ['subscribed', 'group_notifications', 'event_notifications', 'draw_participation', 'gender',
                  'contact_phone']


class AddEmailForm(forms.ModelForm):
    def __init__(self, person, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance.person = person
        self.fields['address'].label = _("Nouvelle adresse")
        self.fields['address'].help_text = _("Utiliser ce champ pour ajouter une adresse supplémentaire que vous pouvez"
                                             " utiliser pour vous connecter.")
        self.fields['address'].error_messages['unique'] = _("Cette adresse est déjà rattaché à un autre compte.")

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Ajouter'))

    class Meta:
        model = PersonEmail
        fields = ("address",)


class SendValidationSMSForm(forms.ModelForm):
    error_messages = {
        'french_only': "Le numéro doit être un numéro de téléphone français.",
        'mobile_only': "Vous devez donner un numéro de téléphone mobile.",
        'rate_limited': "Trop de SMS envoyés. Merci de réessayer dans quelques minutes.",
        'sending_error': "Le SMS n'a pu être envoyé suite à un problème technique. Merci de réessayer plus tard.",
        'already_used': "Ce numéro a déjà été utilisé pour voter. Si vous le partagez avec une autre"
                        " personne, <a href=\"{}\">vous pouvez"
                        " exceptionnellement en demander le déblocage</a>.",
    }

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

        fields = [
            Row(HalfCol(FieldWithButtons(
                'contact_phone',
                Submit('submit', 'Recevoir mon code')
            )))
        ]
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(*fields)

    def clean_phone_number(self):
        return normalize_mobile_phone(self.cleaned_data['contact_phone'], self.error_messages)

    def send_code(self):
        try:
            return send_new_code(self.instance)
        except RateLimitedException:
            self.add_error('contact_phone', self.error_messages['rate_limited'])
            return None
        except SMSSendException:
            self.add_error('contact_phone', self.error_messages['sending_error'])

    class Meta:
        model = Person
        fields = ('contact_phone',)


class CodeValidationForm(Form):
    code = CharField(label=_("Code reçu par SMS"))

    def __init__(self, *args, person, **kwargs):
        super().__init__(*args, **kwargs)
        self.person = person

        fields = [
            Row(HalfCol(FieldWithButtons(
                'code',
                Submit('submit', 'Valider mon numéro')
            )))
        ]
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(*fields)

    def clean_code(self):
        # remove spaces added by Cleave.js
        code = self.cleaned_data['code'].replace(' ', '')

        try:
            if is_valid_code(self.person, code):
                return code
        except RateLimitedException:
            raise ValidationError('Trop de tentative échouées. Veuillez patienter une minute par mesure de sécurité.')

        codes = [code['code'] for code in PersonValidationSMS.objects.values('code').filter(person=self.person,
                                                                  created__gt=timezone.now() - timedelta(
                                                                      minutes=30))]
        logger.warning(
            f"{self.person.email} SMS code failure : tried {self.cleaned_data['code']} and valid"
            f" codes were {', '.join(codes)}"
        )

        if len(code) == 5:
            raise ValidationError('Votre code est incorrect. Attention : le code demandé figure '
                                  'dans le SMS et comporte 6 chiffres. Ne le confondez pas avec le numéro court '
                                  'de l\'expéditeur (5 chiffres).')

        raise ValidationError('Votre code est incorrect ou expiré.')


