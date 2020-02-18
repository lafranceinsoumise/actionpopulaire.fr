from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from agir.donations import tasks
from agir.system_pay.models import SystemPaySubscription


class Command(BaseCommand):
    def handle(self,):
        if now().month == (now() + timedelta(days=7)).month:
            # seulement le dernier dimanche du mois
            return

        for s in SystemPaySubscription.objects.filter(
            active=True,
            alias__expiry_date__lt=now() + timedelta(days=8),
            alias__expiry_date__gt=now() - timedelta(days=32),
        ).distinct("id"):
            tasks.send_expiration_email_reminder.delay(s.pk)
            tasks.send_expiration_sms_reminder.delay(s.pk)
