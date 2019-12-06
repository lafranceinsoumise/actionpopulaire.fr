from django.apps import AppConfig


class TelegramConfig(AppConfig):
    name = "agir.telegram"

    def ready(self):
        from . import signals
