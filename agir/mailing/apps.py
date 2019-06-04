from django.apps import AppConfig


class MailingConfig(AppConfig):
    name = "agir.mailing"

    def ready(self):
        from . import signals
