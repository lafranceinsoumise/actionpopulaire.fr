from datetime import datetime

from django.core.validators import EmailValidator
from django.db.models import Case, When, Value, BooleanField, Count, Q

from agir.people.models import PersonEmail


class BlackListEmailValidator(EmailValidator):
    def validate_domain_part(self, domain_part):
        stats = (
            PersonEmail.objects.filter(address__endswith="@" + domain_part)
            .annotate(
                new=Case(
                    When(person__created__gt=datetime(2020, 11, 8), then=Value(True)),
                    output_field=BooleanField(),
                )
            )
            .aggregate(
                count_apres=Count("id", filter=Q(new=True)),
                count_avant=Count("id", filter=Q(new=None)),
            )
        )
        if stats["count_apres"] > 2 and stats["count_avant"] < 20:
            return False
