from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Row, Div, Submit, Layout
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from agir.lib.form_components import HalfCol
from agir.lib.form_mixins import TagMixin
from agir.people.models import PersonTag, Person, PersonEmail


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

        email_management_link = HTML(block_template.format(
            label=_("Gérez vos adresses emails"),
            value=format_html(
                '<a href="{}" class="btn btn-default">{}</a>',
                reverse('email_management'),
                _("Accéder au formulaire de gestion de vos emails"),
            ),
            help_text=_("Ce formulaire vous permet d'ajouter de nouvelles adresses ou de supprimer les existantes"),
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
                        HalfCol(email_management_link)
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
                    HalfCol(email_management_link)
                )
            ))

        fields.extend([
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
        fields = ['subscribed', 'group_notifications', 'event_notifications', 'draw_participation', 'gender']


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
