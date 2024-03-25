from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.db import transaction
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from agir.groups.actions.notifications import new_message_notifications
from agir.groups.models import SupportGroup
from agir.lib import data
from agir.msgs.models import SupportGroupMessage, MessageAttachment
from agir.people.models import Person
from agir.people.person_forms.fields import FileField


class AdminSupportGroupMessage:
    DEFAULTS = {"is_locked": True, "readonly": True}

    def __init__(self, message, attachment, supportgroups):
        self.attachment = attachment
        self.instances = []
        for supportgroup in supportgroups:
            self.instances.append(self.get_message_for_group(message, supportgroup))

    def format_message_text(self, message):
        group_data = {
            "[groupe_id]": str(message.supportgroup.id),
            "[groupe_nom]": str(message.supportgroup.name),
        }

        for var, val in group_data.items():
            message.subject = message.subject.replace(var, val)
            message.text = message.text.replace(var, val)

        return message

    def get_message_for_group(self, message, supportgroup):
        message = SupportGroupMessage(
            **self.DEFAULTS,
            author=message.author,
            supportgroup=supportgroup,
            required_membership_type=message.required_membership_type,
            subject=message.subject,
            text=message.text,
        )
        return self.format_message_text(message)

    def save(self):
        with transaction.atomic():
            if self.attachment:
                attachment = MessageAttachment.objects.create(
                    name=self.attachment.name, file=self.attachment
                )
                for instance in self.instances:
                    instance.attachment = attachment

            self.instances = SupportGroupMessage.objects.bulk_create(self.instances)

            for instance in self.instances:
                new_message_notifications(instance)

            return self.instances


class SupportGroupMessageCreateForm(forms.ModelForm):
    AUTHOR_CHOICES = Person.objects.filter(public_email__address=settings.EMAIL_SUPPORT)
    author = forms.ModelChoiceField(
        AUTHOR_CHOICES,
        required=True,
        label=_("Auteur·ice"),
        disabled=True,
        initial=AUTHOR_CHOICES.first,
    )

    SUPPORTGROUP_CHOICES = SupportGroup.objects.active().filter(
        is_private_messaging_enabled=True
    )
    supportgroups = forms.ModelMultipleChoiceField(
        SUPPORTGROUP_CHOICES,
        required=False,
        label=_("Groupes destinataires"),
        widget=AutocompleteSelectMultiple(
            SupportGroupMessage._meta.get_field("supportgroup"), admin.site
        ),
        help_text=_(
            "Vous pouvez spécifier ici une liste de groupes destinataires du message. Vous pouvez laisser ce champ "
            "vide pour sélectionner les destinataires uniquement sur la base des autres champs "
            "(type et/ou certification)."
        ),
    )

    SUPPORTGROUP_TYPE_CHOICES = (("", ""), *SupportGroup.TYPE_CHOICES)
    supportgroup_type = forms.ChoiceField(
        choices=SUPPORTGROUP_TYPE_CHOICES,
        required=False,
        label=_("Type de groupe"),
    )

    CERTIFIED_CHOICES = (
        ("", ""),
        (True, "Uniquement les groupes certifiés"),
        (False, "Uniquement les groupes non certifiés"),
    )
    certified = forms.TypedChoiceField(
        choices=CERTIFIED_CHOICES,
        coerce=lambda x: x == "True",
        empty_value="",
        required=False,
        label=_("Certification"),
    )

    departements = forms.MultipleChoiceField(
        choices=data.departements_choices, required=False, label=_("Département")
    )

    attachment_file = FileField(
        label=_("Pièce-jointe"),
        required=False,
        allow_empty_file=False,
        max_size=MessageAttachment.MAX_SIZE,
        allowed_extensions=MessageAttachment.ALLOWED_EXTENSIONS,
        help_text=f"""
        Taille maximale : {filesizeformat(MessageAttachment.MAX_SIZE)}<br />
        Extensions acceptées : {", ".join(MessageAttachment.ALLOWED_EXTENSIONS)}.
        """,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].required = True
        self.fields["subject"].help_text = self.fields["text"].help_text = mark_safe(
            _(
                "Les variables <code>[groupe_id]</code> et <code>[groupe_nom]</code> peuvent être utilisées dans le "
                "texte et seront remplacées automatiquement pour chaque groupe destinataire."
            )
        )

    def clean(self):
        data = super().clean()

        supportgroups = data.get("supportgroups")
        supportgroup_type = data.get("supportgroup_type", "")
        certified = data.get("certified", "")

        if not supportgroups and not supportgroup_type and not certified:
            error = _(
                "Veuillez choisir au moins un critère de sélection de groupes destinataires"
            )
            self._errors["supportgroups"] = self.error_class([error])
            self._errors["supportgroup_type"] = self.error_class([error])
            self._errors["certified"] = self.error_class([error])

        if not supportgroups:
            supportgroups = SupportGroup.objects.active().filter(
                is_private_messaging_enabled=True
            )
        if supportgroup_type:
            supportgroups = supportgroups.filter(type=data["supportgroup_type"])
        if certified is True:
            supportgroups = supportgroups.certified()
        if certified is False:
            supportgroups = supportgroups.uncertified()

        if not supportgroups:
            error = _("Aucun groupe n'a été trouvé avec les filtres sélectionnés")
            for field in ("supportgroups", "supportgroup_type", "certified"):
                if data.get(field, None):
                    self._errors[field] = self.error_class([error])

        data["supportgroups"] = supportgroups

        return data

    def save(self, commit=True):
        return AdminSupportGroupMessage(
            self.instance,
            self.cleaned_data.get("attachment_file"),
            self.cleaned_data.get("supportgroups"),
        ).save()

    class Meta:
        model = SupportGroupMessage
        fields = (
            "supportgroups",
            "supportgroup_type",
            "certified",
            "required_membership_type",
            "author",
            "subject",
            "text",
            "attachment_file",
        )
        fieldsets = (
            (
                "Message",
                {
                    "description": mark_safe(
                        _(
                            "Vous pouvez envoyer un message à un ou plusieurs groupes d'actions. Les destinataires "
                            "du message recevront une notification les informant de la reception du message. Il ne "
                            "sera pas possible de répondre au message."
                        )
                    ),
                    "fields": (
                        "author",
                        "subject",
                        "text",
                        "attachment_file",
                    ),
                },
            ),
            (
                "Groupes destinataires",
                {
                    "description": mark_safe(
                        _(
                            "Grâce aux champs ci-dessous, vous pouvez choisir les groupes auxquels envoyer le "
                            "message. Au moins un des critères <em>Groupes destinataires</em>, <em>Type de groupe</em> "
                            "et <em>Certification</em> doit être sélectionné pour pouvoir valider l'envoi."
                        )
                    ),
                    "fields": (
                        "supportgroups",
                        "supportgroup_type",
                        "certified",
                        "required_membership_type",
                    ),
                },
            ),
        )
