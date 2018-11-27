from django.apps import AppConfig


class PeopleConfig(AppConfig):
    name = "agir.people"

    def ready(self):
        from . import signals
