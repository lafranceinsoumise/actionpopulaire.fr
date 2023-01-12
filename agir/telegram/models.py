from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from pyrogram import Client

from agir.lib.models import TimeStampedModel

api_params = {
    "api_id": settings.TELEGRAM_API_ID,
    "api_hash": settings.TELEGRAM_API_HASH,
    "no_updates": True,
}

TELEGRAM_META_KEY = "has_telegram"


class TelegramSession(TimeStampedModel, models.Model):
    phone_number = PhoneNumberField("Numéro de téléphone", unique=True)
    session_string = models.TextField("Chaîne de session", editable=False, blank=True)

    def create_client(self):
        if self.session_string:
            return Client(
                f"session-{self.phone_number}",
                session_string=self.session_string,
                **api_params,
            )

    def __str__(self):
        return str(self.phone_number)


class TelegramGroup(TimeStampedModel, models.Model):
    CHAT_TYPE_CHANNEL = "channel"
    CHAT_TYPE_SUPERGROUP = "supergroup"
    CHAT_TYPE_CHOICES = (
        (CHAT_TYPE_CHANNEL, "Channel"),
        (CHAT_TYPE_SUPERGROUP, "Supergroupe"),
    )

    name = models.CharField("Nom du groupe / channel", max_length=100)
    telegram_ids = ArrayField(
        models.BigIntegerField(editable=False, null=True),
        verbose_name="Identifiants des groupes sur Telegram",
        default=list,
    )
    type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES)
    admin_session = models.ForeignKey(
        "TelegramSession",
        related_name="groups",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="La session Telegram admin de ce groupe.",
    )
    telegram_users = models.PositiveSmallIntegerField(
        "Nombre d'utilisateurices de Telegram dans le segment", blank=True, default=0
    )
    segment = models.ForeignKey(
        "mailing.Segment",
        related_name="telegram_groups",
        on_delete=models.PROTECT,
        verbose_name="Le segment sur lequel se baser pour constituer la liste.",
    )

    def __str__(self):
        return self.name
