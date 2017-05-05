from django.apps import AppConfig


class ClientsConfig(AppConfig):
    name = 'clients'

    def ready(self):
        from . import signals
