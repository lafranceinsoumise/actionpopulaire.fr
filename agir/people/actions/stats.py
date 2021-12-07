import statistics
from datetime import timedelta

from django.conf import settings
from django.db.models import Count, IntegerField, ExpressionWrapper
from django.db.models.functions import ExtractYear
from django.utils import timezone
from push_notifications.models import GCMDevice, APNSDevice

from agir.groups.models import Membership
from agir.payments.models import Payment
from agir.people.models import Person
from agir.presidentielle2022.apps import Presidentielle2022Config


def get_statistics_for_queryset(original_queryset):
    current_year = timezone.now().year
    person_pks = original_queryset.values_list("pk", flat=True)
    queryset = Person.objects.filter(pk__in=person_pks)

    stats = {"total": len(person_pks)}

    group_members = (
        Membership.objects.filter(
            person_id__in=person_pks,
            membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER,
            supportgroup__published=True,
        )
        .values("person_id")
        .distinct()
    )
    stats["group_members"] = group_members.count()
    stats["group_referents"] = group_members.filter(
        membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
    ).count()
    stats["certified_group_members"] = group_members.filter(
        supportgroup__subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES,
    ).count()

    stats["is_2022"] = queryset.filter(is_2022=True).count()
    stats["is_insoumise"] = queryset.filter(is_insoumise=True).count()
    donors = (
        Payment.objects.filter(
            person_id__in=person_pks,
        )
        .values("person_id")
        .distinct()
    )
    stats["is_2022_donors"] = donors.filter(
        type__in=[
            Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
        ],
    ).count()
    stats["is_insoumise_donors"] = donors.exclude(
        type__in=[
            Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
        ],
    ).count()
    stats["liaisons"] = queryset.liaisons().count()
    stats["contacts"] = queryset.filter(
        meta__subscriptions__AP__subscriber__isnull=False
    ).count()
    stats["elected_representatives"] = queryset.elus().count()

    ages = (
        queryset.filter(date_of_birth__isnull=False)
        .annotate(
            age=ExpressionWrapper(
                current_year - ExtractYear("date_of_birth"),
                output_field=IntegerField(),
            )
        )
        .order_by("age")
        .values_list("age", flat=True)
    )
    stats["known_birthdates"] = len(ages)
    if len(ages) > 0:
        stats["mean_age"] = statistics.mean(ages)
        stats["median_age"] = statistics.median(ages)

    stats["known_phone_numbers"] = (
        queryset.filter(contact_phone__isnull=False).exclude(contact_phone="").count()
    )

    stats["newsletter_subscribers"] = queryset.filter(newsletters__len__gt=0).count()
    stats["sms_subscribers"] = queryset.filter(subscribed_sms=True).count()

    stats["android_users"] = (
        GCMDevice.objects.filter(active=True, user__person__id__in=person_pks)
        .values("user_id")
        .distinct()
        .count()
    )

    stats["ios_users"] = (
        APNSDevice.objects.filter(active=True, user__person__id__in=person_pks)
        .values("user_id")
        .distinct()
        .count()
    )

    stats["zip_codes"] = [
        (row["location_zip"], row["count"])
        for row in (
            queryset.filter(location_zip__isnull=False)
            .exclude(location_zip__iexact="")
            .values("location_zip")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
    ]

    stats["last_week_connections"] = queryset.filter(
        role__last_login__date__gte=(timezone.now() - timedelta(days=7)).date()
    ).count()

    return stats
