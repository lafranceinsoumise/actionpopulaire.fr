from django.core.management import BaseCommand
from pyrogram import Client

from agir.lib.management_utils import person_argument
from agir.lib.phone_numbers import is_mobile_number
from agir.telegram.models import api_params, TelegramSession


class Command(BaseCommand):
    help = "Create a Telegram Session for a user"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument("phone_number", type=str)

    def handle(self, phone_number, **options):
        if not is_mobile_number(phone_number):
            raise ValueError("La personne doit avoir un numéro de téléphone mobile.")

        try:
            TelegramSession.objects.get(phone_number=phone_number)
            raise ValueError("Ce numéro a déjà une session Telegram enregistrée.")
        except TelegramSession.DoesNotExist:
            pass

        client = Client(":memory:", phone_number=str(phone_number), **api_params)
        client.start()
        session_string = client.export_session_string()
        TelegramSession.objects.create(phone_number, session_string=session_string)

        print("OK !")
        client.stop()
