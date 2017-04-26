from django.apps import AppConfig


class PeopleConfig(AppConfig):
    name = 'people'

    def ready(self):
        from . import signals
