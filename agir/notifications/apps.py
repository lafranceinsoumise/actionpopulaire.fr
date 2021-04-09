from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "agir.notifications"

    def ready(self):
        from agir.notifications import signals
