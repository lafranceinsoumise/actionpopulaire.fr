from django.core.management import BaseCommand
from pyrogram import Client

from agir.lib.management_utils import phone_argument
from agir.lib.phone_numbers import is_mobile_number
from agir.telegram.models import api_params, TelegramSession


class Command(BaseCommand):
    help = "Create a Telegram Session with a phone number"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument("phone_number", type=phone_argument)

    def handle(self, phone_number, **options):
        if not is_mobile_number(phone_number):
            raise ValueError("Le numéro doit être un numéro de téléphone mobile.")

        (session, created) = TelegramSession.objects.get_or_create(
            phone_number=phone_number
        )

        client = Client(
            f"session-{session.phone_number}",
            in_memory=True,
            phone_number=str(phone_number),
            **api_params,
        )
        with client:
            session_string = client.export_session_string()
            session.session_string = session_string
            session.save()
