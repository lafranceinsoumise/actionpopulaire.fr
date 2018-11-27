from django.apps import AppConfig


class ClientsConfig(AppConfig):
    name = "agir.clients"

    def ready(self):
        from . import signals
