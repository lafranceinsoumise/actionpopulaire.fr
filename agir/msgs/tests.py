from rest_framework.test import APITestCase

from agir.groups.models import SupportGroup, Membership
from agir.msgs.models import UserReport, SupportGroupMessage
from agir.people.models import Person


class GroupMessagesTestAPICase(APITestCase):
    def setUp(self):
        self.manager = Person.objects.create(
            email="member@example.com", create_role=True,
        )
        self.group = SupportGroup.objects.create()
        Membership.objects.create(
            person=self.manager,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.message = SupportGroupMessage.objects.create(
            supportgroup=self.group, author=self.manager, text="Lorem"
        )
        self.reporter = Person.objects.create(
            email="reporter@example.com", create_role=True
        )
        self.client.force_login(self.reporter.role)

    def test_can_user_report_message(self):
        res = self.client.post(
            "/api/report/",
            data={
                "content_type": "msgs.supportgroupmessage",
                "object_id": str(self.message.pk),
            },
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(UserReport.objects.first().reported_object, self.message)
