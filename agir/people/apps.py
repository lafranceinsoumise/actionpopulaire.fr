from django.apps import AppConfig


class PeopleConfig(AppConfig):
    name = "agir.people"
    verbose_name = "Personnes"

    def ready(self):
        from . import signals
