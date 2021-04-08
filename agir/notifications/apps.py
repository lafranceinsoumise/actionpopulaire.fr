from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "agir.notifications"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from agir.notifications import signals
