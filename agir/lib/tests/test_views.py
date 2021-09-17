from pathlib import Path

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agir.events.models import Event, OrganizerConfig
from agir.groups.models import SupportGroup, Membership
from agir.people.models import Person

IMG_TEST_DIR = Path(__file__).parent / "data"


class ImageSizeWarningTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "test@test_other.com", create_role=True
        )
        self.role = self.person.role
        self.group = SupportGroup.objects.create(name="Group name")
        Membership.objects.create(
            supportgroup=self.group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        self.day = day = timezone.timedelta(days=1)

        self.organized_event = Event.objects.create(
            name="Organized event", start_time=now + day, end_time=now + 2 * day
        )
        OrganizerConfig.objects.create(
            event=self.organized_event, person=self.person, is_creator=True
        )

        self.past_event = Event.objects.create(
            name="past Event",
            # subtype=self.subtype,
            start_time=now - 2 * day,
            end_time=now - 1 * day,
        )
        OrganizerConfig.objects.create(
            event=self.past_event, person=self.person, is_creator=True
        )
        self.person.save()
