from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import now

# Create your tests here.
from faker import Faker

from agir.elus.models import MandatMunicipal, StatutMandat
from agir.events.models import EventSubtype, Event, RSVP
from agir.groups.models import SupportGroupSubtype, SupportGroup, Membership
from agir.mailing.models import Segment
from agir.people.models import Person, PersonTag, Qualification, PersonQualification

fake = Faker("fr_FR")


class SegmentTestCase(TestCase):
    def setUp(self) -> None:
        self.person_with_account = Person.objects.create_insoumise(
            email="a@a.a",
            create_role=True,
        )

        self.person_without_account = Person.objects.create_person(email="b@b.b")

    def test_default_segment_include_anyone(self):
        s = Segment.objects.create(newsletters=[])

        self.assertIn(self.person_with_account, s.get_people())
        self.assertIn(self.person_without_account, s.get_people())

    def test_person_with_disabled_account_not_in_segment(self):
        s = Segment.objects.create(newsletters=[])
        role = self.person_with_account.role
        role.is_active = False
        role.save()

        self.assertNotIn(self.person_with_account, s.get_people())

    def test_segment_with_registration_duration(self):
        old_person = Person.objects.create_person(
            email="old@agir.local", created=now() - timedelta(hours=2)
        )
        new_person = Person.objects.create_person(email="new@agir.local", created=now())
        s = Segment.objects.create(newsletters=[], registration_duration=1)
        self.assertIn(old_person, s.get_people())
        self.assertNotIn(new_person, s.get_people())


class SegmentEventFilterTestCase(TestCase):
    def create_event(self, start_time=None, end_time=None, subtype=None):
        if start_time is None:
            start_time = timezone.now()
        if end_time is None:
            end_time = start_time + timedelta(minutes=30)
        if subtype is None:
            subtype = self.default_subtype

        event = {"start_time": start_time, "end_time": end_time, "subtype": subtype}
        return Event.objects.create(**event)

    def create_attendee(self, event=None, status=RSVP.Status.CONFIRMED):
        if event is None:
            event = self.default_event
        attendee = Person.objects.create_insoumise(
            email=fake.email(),
            create_role=True,
        )
        RSVP.objects.create(event=event, person=attendee, status=status)
        return attendee

    def create_organizer(self, event=None):
        if event is None:
            event = self.default_event
        organizer = Person.objects.create_insoumise(
            email=fake.email(),
            create_role=True,
        )
        event.organizers.add(organizer)
        return organizer

    def setUp(self):
        self.default_subtype = EventSubtype.objects.create(label="Default subtype")
        self.default_event = self.create_event()

    def test_event_participant_filter(self):
        event = self.create_event()
        includes = [self.create_attendee(event)]
        excludes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
            self.create_attendee(),
            self.create_organizer(),
            self.create_organizer(event),
            self.create_attendee(event, status=RSVP.Status.CANCELLED),
        ]
        s = Segment.objects.create(newsletters=[], events_organizer=False)
        s.events.add(event)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_event_organizer_filter(self):
        event = self.create_event()
        includes = [self.create_organizer(event)]
        excludes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
            self.create_attendee(),
            self.create_organizer(),
            self.create_attendee(event),
        ]
        s = Segment.objects.create(newsletters=[], events_organizer=True)
        s.events.add(event)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_excluded_event_participant_filter(self):
        event = self.create_event()
        includes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
            self.create_attendee(),
            self.create_organizer(),
            self.create_organizer(event),
            self.create_attendee(event, status=RSVP.Status.CANCELLED),
        ]
        excludes = [self.create_attendee(event)]
        s = Segment.objects.create(
            newsletters=[],
        )
        s.excluded_events.add(event)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_excluded_event_organizer_filter(self):
        event = self.create_event()
        includes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
            self.create_attendee(),
            self.create_organizer(),
            self.create_attendee(event),
        ]
        excludes = [self.create_organizer(event)]
        s = Segment.objects.create(newsletters=[], events_organizer=True)
        s.excluded_events.add(event)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_event_subtype_participant_filter(self):
        subtype = EventSubtype.objects.create(label="Sub")
        event = self.create_event(subtype=subtype)
        includes = [self.create_attendee(event)]
        excludes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
            self.create_attendee(),
            self.create_organizer(),
            self.create_organizer(event),
            self.create_attendee(event, status=RSVP.Status.CANCELLED),
        ]
        s = Segment.objects.create(
            newsletters=[],
        )
        s.events_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_event_subtype_organizer_filter(self):
        subtype = EventSubtype.objects.create(label="Sub")
        event = self.create_event(subtype=subtype)
        includes = [
            self.create_organizer(event),
        ]
        excludes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
            self.create_attendee(),
            self.create_organizer(),
            self.create_attendee(event),
            self.create_attendee(event, status=RSVP.Status.CANCELLED),
        ]
        s = Segment.objects.create(newsletters=[], events_organizer=True)
        s.events_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_event_time_range_participant_filter(self):
        start_time = timezone.now() - timedelta(days=150)
        end_time = start_time + timedelta(minutes=30)
        event = self.create_event(start_time=start_time, end_time=end_time)
        includes = [self.create_attendee(event)]
        excludes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
            self.create_attendee(),
            self.create_organizer(),
            self.create_organizer(event),
            self.create_attendee(event, status=RSVP.Status.CANCELLED),
        ]
        s = Segment.objects.create(
            newsletters=[],
            events_start_date=timezone.now() - timedelta(days=200),
            events_end_date=timezone.now() - timedelta(days=100),
        )
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_event_time_range_organizer_filter(self):
        start_time = timezone.now() - timedelta(days=150)
        end_time = start_time + timedelta(minutes=30)
        event = self.create_event(start_time=start_time, end_time=end_time)
        includes = [self.create_organizer(event)]
        excludes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
            self.create_attendee(),
            self.create_organizer(),
            self.create_attendee(event),
            self.create_attendee(event, status=RSVP.Status.CANCELLED),
        ]
        s = Segment.objects.create(
            newsletters=[],
            events_organizer=True,
            events_start_date=timezone.now() - timedelta(days=200),
            events_end_date=timezone.now() - timedelta(days=100),
        )
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())


class SegmentSupportgroupFilterTestCase(TestCase):
    def create_group(self, subtype=None, **kwargs):
        if subtype is None:
            subtype = self.default_subtype
        kwargs["name"] = f"Groupe de {fake.city()}"
        group = SupportGroup.objects.create(**kwargs)
        group.subtypes.add(subtype)

        return group

    def create_member(
        self, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER, supportgroup=None
    ):
        if supportgroup is None:
            supportgroup = self.default_group
        member = Person.objects.create_insoumise(
            email=fake.email(),
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=supportgroup, person=member, membership_type=membership_type
        )

        return member

    def create_manager(self, *args, **kwargs):
        return self.create_member(
            *args, membership_type=Membership.MEMBERSHIP_TYPE_MANAGER, **kwargs
        )

    def create_referent(self, *args, **kwargs):
        return self.create_member(
            *args, membership_type=Membership.MEMBERSHIP_TYPE_REFERENT, **kwargs
        )

    def setUp(self):
        self.default_subtype = SupportGroupSubtype.objects.create(label="default")
        self.default_group = self.create_group(subtype=self.default_subtype)

    def test_default_segment_include_anyone(self):
        certified_group = self.create_group(certification_date=timezone.now())
        uncertified_group = self.create_group(certification_date=None)
        includes = [
            self.create_member(),
            self.create_member(supportgroup=certified_group),
            self.create_member(supportgroup=uncertified_group),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(newsletters=[])
        for person in includes:
            self.assertIn(person, s.get_people())

    def test_supportgroup_status_not_member_filter(self):
        supportgroup = self.create_group()
        includes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        excludes = [
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            self.create_referent(),
            self.create_referent(supportgroup=supportgroup),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_status=Segment.GA_STATUS_NOT_MEMBER,
        )
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_status_member_filter(self):
        supportgroup = self.create_group()
        includes = [
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            self.create_referent(),
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_status=Segment.GA_STATUS_MEMBER,
        )
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_status_manager_filter(self):
        supportgroup = self.create_group()
        includes = [
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            self.create_referent(),
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_status=Segment.GA_STATUS_MANAGER,
        )
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_status_referent_filter(self):
        supportgroup = self.create_group()
        includes = [
            self.create_referent(),
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_status=Segment.GA_STATUS_REFERENT,
        )
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroups_filter(self):
        supportgroup = self.create_group()
        includes = [self.create_member(supportgroup=supportgroup)]
        excludes = [
            self.create_member(),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(newsletters=[])
        s.supportgroups.add(supportgroup)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_status_and_supportgroups_filter_combo(self):
        supportgroup = self.create_group()
        includes = [
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_referent(),
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_status=Segment.GA_STATUS_REFERENT,
        )
        s.supportgroups.add(supportgroup)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_subtypes_filter(self):
        subtype = SupportGroupSubtype.objects.create(label="filtered")
        supportgroup = self.create_group(subtype=subtype)
        includes = [self.create_member(supportgroup=supportgroup)]
        excludes = [
            self.create_member(),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(newsletters=[])
        s.supportgroup_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_status_and_supportgroup_subtypes_filter_combo(self):
        subtype = SupportGroupSubtype.objects.create(label="filtered")
        supportgroup = self.create_group(subtype=subtype)
        includes = [
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_referent(),
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_status=Segment.GA_STATUS_REFERENT,
        )
        s.supportgroup_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroups_overrides_supportgroup_subtypes_filter(self):
        subtype = SupportGroupSubtype.objects.create(label="filtered")
        subtype_supportgroup = self.create_group(subtype=subtype)
        another_supportgroup = self.create_group()
        includes = [self.create_member(supportgroup=another_supportgroup)]
        excludes = [self.create_member(supportgroup=subtype_supportgroup)]
        s = Segment.objects.create(newsletters=[])
        s.supportgroups.add(another_supportgroup)
        s.supportgroup_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_is_certified_filter(self):
        certified_supportgroup = self.create_group(certification_date=timezone.now())
        uncertified_supportgroup = self.create_group(certification_date=None)
        includes = [self.create_member(supportgroup=certified_supportgroup)]
        excludes = [
            self.create_member(),
            self.create_member(supportgroup=uncertified_supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(newsletters=[], supportgroup_is_certified=True)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_status_and_supportgroup_subtypes_filter_combo(self):
        subtype = SupportGroupSubtype.objects.create(label="filtered")
        supportgroup = self.create_group(subtype=subtype)
        includes = [
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_referent(),
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_status=Segment.GA_STATUS_REFERENT,
        )
        s.supportgroup_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_types_filter(self):
        local_group = self.create_group(type=SupportGroup.TYPE_LOCAL_GROUP)
        thematic_group = self.create_group(type=SupportGroup.TYPE_THEMATIC)
        includes = [self.create_member(supportgroup=local_group)]
        excludes = [
            self.create_member(supportgroup=thematic_group),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_types=[SupportGroup.TYPE_LOCAL_GROUP],
        )
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())

    def test_supportgroup_types_and_supportgroups_filter_combo(self):
        subtype = SupportGroupSubtype.objects.create(
            label="filtered", type=SupportGroup.TYPE_LOCAL_GROUP
        )
        local_group = self.create_group(
            type=SupportGroup.TYPE_LOCAL_GROUP, subtype=subtype
        )
        thematic_group = self.create_group(type=SupportGroup.TYPE_THEMATIC)
        another_local_group = self.create_group(type=SupportGroup.TYPE_LOCAL_GROUP)
        includes = [
            self.create_member(supportgroup=local_group),
            self.create_referent(supportgroup=local_group),
        ]
        excludes = [
            self.create_member(supportgroup=another_local_group),
            self.create_manager(supportgroup=another_local_group),
            self.create_member(supportgroup=thematic_group),
            self.create_manager(supportgroup=thematic_group),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            supportgroup_types=[SupportGroup.TYPE_LOCAL_GROUP],
        )
        s.supportgroup_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_people())
        for person in excludes:
            self.assertNotIn(person, s.get_people())


class SegmentTagFilterTestCase(TestCase):
    def create_tag(self, **kwargs):
        kwargs["label"] = kwargs.get("label", self.tag_labels.pop())
        tag = PersonTag.objects.create(**kwargs)

        return tag

    def create_person(self, with_tags=None):
        person = Person.objects.create_insoumise(
            email=fake.email(),
            create_role=True,
        )
        if isinstance(with_tags, list):
            person.tags.add(*with_tags)

        return person

    def setUp(self):
        self.tag_labels = fake.words(nb=100, unique=True)
        self.default_tag = self.create_tag()
        self.untagged_person = self.create_person()
        self.default_tagged_person = self.create_person(with_tags=self.default_tag)

    def test_default_segment_include_anyone(self):
        includes = [
            self.untagged_person,
            self.default_tagged_person,
        ]
        s = Segment.objects.create(newsletters=[])
        for person in includes:
            self.assertIn(person, s.get_people())

    def test_tag_whitelist_segment(self):
        ok_tag = self.create_tag()
        ko_tag = self.create_tag()

        includes = [
            self.create_person(with_tags=[ok_tag]),
            self.create_person(with_tags=[ok_tag, ko_tag]),
        ]
        excludes = [
            self.untagged_person,
            self.default_tagged_person,
            self.create_person(with_tags=[ko_tag]),
        ]
        s = Segment.objects.create(newsletters=[])
        s.tags.add(ok_tag)

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_tag_blacklist_segment(self):
        forbidden_tag = self.create_tag()
        another_tag = self.create_tag()

        includes = [
            self.untagged_person,
            self.default_tagged_person,
            self.create_person(with_tags=[another_tag]),
        ]
        excludes = [
            self.create_person(with_tags=[forbidden_tag]),
            self.create_person(with_tags=[forbidden_tag, another_tag]),
        ]

        s = Segment.objects.create(newsletters=[])
        s.excluded_tags.add(forbidden_tag)

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_tag_whitelist_and_blacklist_segment(self):
        forbidden_tag = self.create_tag()
        selected_tag = self.create_tag()
        forbidden_and_selected_tag = self.create_tag()
        another_tag = self.create_tag()

        includes = [
            self.create_person(with_tags=[selected_tag]),
            self.create_person(with_tags=[selected_tag, another_tag]),
        ]
        excludes = [
            self.untagged_person,
            self.default_tagged_person,
            self.create_person(with_tags=[forbidden_tag]),
            self.create_person(with_tags=[forbidden_tag, selected_tag]),
            self.create_person(with_tags=[forbidden_and_selected_tag]),
        ]

        s = Segment.objects.create(newsletters=[])
        s.tags.add(selected_tag, forbidden_and_selected_tag)
        s.excluded_tags.add(forbidden_tag, forbidden_and_selected_tag)

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)


class SegmentQualificationFilterTestCase(TestCase):
    def create_qualification(self, **kwargs):
        kwargs["label"] = kwargs.get("label", fake.job()[:50])
        qualification = Qualification.objects.create(**kwargs)

        return qualification

    def create_person(self, qualification=None, status=None):
        person = Person.objects.create_insoumise(
            email=fake.email(),
            create_role=True,
        )

        if not qualification:
            return person

        if not status:
            PersonQualification.objects.create(
                person=person,
                qualification=qualification,
            )
            return person

        now = timezone.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        if status == PersonQualification.Status.EFFECTIVE:
            PersonQualification.objects.create(
                person=person,
                qualification=qualification,
                start_time=yesterday,
                end_time=tomorrow,
            )
        elif status == PersonQualification.Status.PAST:
            PersonQualification.objects.create(
                person=person, qualification=qualification, end_time=yesterday
            )
        elif status == PersonQualification.Status.FUTURE:
            PersonQualification.objects.create(
                person=person,
                qualification=qualification,
                start_time=tomorrow,
            )

        return person

    def setUp(self):
        self.default_qualification = self.create_qualification()
        self.unqualified_person = self.create_person()
        self.default_qualified_person = self.create_person(
            qualification=self.default_qualification
        )

    def test_default_segment_include_anyone(self):
        includes = [
            self.unqualified_person,
            self.default_qualified_person,
        ]
        s = Segment.objects.create(newsletters=[])
        for person in includes:
            self.assertIn(person, s.get_people())

    def test_qualification_whitelist_segment(self):
        ok_qualification = self.create_qualification()
        ko_qualification = self.create_qualification()

        includes = [
            self.create_person(qualification=ok_qualification),
        ]
        excludes = [
            self.unqualified_person,
            self.default_qualified_person,
            self.create_person(qualification=ko_qualification),
        ]
        s = Segment.objects.create(newsletters=[])
        s.qualifications.add(ok_qualification)

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_qualification_all_statuses_segment(self):
        ok_qualification = self.create_qualification()
        ko_qualification = self.create_qualification()

        includes = [
            self.create_person(qualification=ok_qualification),
            self.create_person(
                qualification=ok_qualification, status=PersonQualification.Status.PAST
            ),
            self.create_person(
                qualification=ok_qualification,
                status=PersonQualification.Status.EFFECTIVE,
            ),
            self.create_person(
                qualification=ok_qualification, status=PersonQualification.Status.FUTURE
            ),
        ]
        excludes = [
            self.unqualified_person,
            self.default_qualified_person,
            self.create_person(qualification=ko_qualification),
        ]
        s = Segment.objects.create(newsletters=[], person_qualification_status=[])
        s.qualifications.add(ok_qualification)

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

        s.person_qualification_status = PersonQualification.Status.values
        s.save()

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_past_qualification_segment(self):
        ok_qualification = self.create_qualification()
        ko_qualification = self.create_qualification()

        includes = [
            self.create_person(
                qualification=ok_qualification, status=PersonQualification.Status.PAST
            ),
        ]
        excludes = [
            self.unqualified_person,
            self.default_qualified_person,
            self.create_person(qualification=ko_qualification),
            self.create_person(qualification=ok_qualification),
            self.create_person(
                qualification=ok_qualification,
                status=PersonQualification.Status.EFFECTIVE,
            ),
            self.create_person(
                qualification=ok_qualification, status=PersonQualification.Status.FUTURE
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            person_qualification_status=[PersonQualification.Status.PAST],
        )
        s.qualifications.add(ok_qualification)

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_effective_qualification_segment(self):
        ok_qualification = self.create_qualification()
        ko_qualification = self.create_qualification()

        includes = [
            self.create_person(qualification=ok_qualification),
            self.create_person(
                qualification=ok_qualification,
                status=PersonQualification.Status.EFFECTIVE,
            ),
        ]
        excludes = [
            self.unqualified_person,
            self.default_qualified_person,
            self.create_person(qualification=ko_qualification),
            self.create_person(
                qualification=ok_qualification, status=PersonQualification.Status.PAST
            ),
            self.create_person(
                qualification=ok_qualification, status=PersonQualification.Status.FUTURE
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            person_qualification_status=[PersonQualification.Status.EFFECTIVE],
        )
        s.qualifications.add(ok_qualification)

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_future_qualification_segment(self):
        ok_qualification = self.create_qualification()
        ko_qualification = self.create_qualification()

        includes = [
            self.create_person(
                qualification=ok_qualification, status=PersonQualification.Status.FUTURE
            ),
        ]
        excludes = [
            self.unqualified_person,
            self.default_qualified_person,
            self.create_person(qualification=ko_qualification),
            self.create_person(qualification=ok_qualification),
            self.create_person(
                qualification=ok_qualification,
                status=PersonQualification.Status.EFFECTIVE,
            ),
            self.create_person(
                qualification=ok_qualification, status=PersonQualification.Status.PAST
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            person_qualification_status=[PersonQualification.Status.FUTURE],
        )
        s.qualifications.add(ok_qualification)

        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)


class SegmentMandatFilterTestCase(TestCase):
    def create_person(self, **kwargs):
        person = Person.objects.create_insoumise(
            email=fake.email(), create_role=True, **kwargs
        )
        return person

    def create_mandat(
        self,
        model=MandatMunicipal,
        person=None,
        membre_reseau_elus=Person.MEMBRE_RESEAU_INCONNU,
        **kwargs,
    ):
        if person is None:
            person = self.create_person(membre_reseau_elus=membre_reseau_elus)

        model.objects.create(person=person, **kwargs)

        return person

    def setUp(self):
        self.unelected_person = self.create_person()
        self.elected_person = self.create_mandat()

    def test_default_segment_include_anyone(self):
        includes = [
            self.unelected_person,
            self.elected_person,
        ]
        s = Segment.objects.create(newsletters=[])
        for person in includes:
            self.assertIn(person, s.get_people())

    def test_elu_ELUS_MEMBRE_RESEAU_segment(self):
        includes = [self.create_mandat(membre_reseau_elus=Person.MEMBRE_RESEAU_OUI)]
        excludes = [
            self.unelected_person,
            self.create_mandat(membre_reseau_elus=Person.MEMBRE_RESEAU_NON),
            self.create_mandat(
                membre_reseau_elus=Person.MEMBRE_RESEAU_OUI, statut=StatutMandat.FAUX
            ),
        ]
        s = Segment.objects.create(newsletters=[], elu=Segment.ELUS_MEMBRE_RESEAU)
        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_elu_ELUS_REFERENCE_segment(self):
        includes = [
            self.create_mandat(membre_reseau_elus=Person.MEMBRE_RESEAU_OUI),
        ]
        excludes = [
            self.unelected_person,
            self.create_mandat(membre_reseau_elus=Person.MEMBRE_RESEAU_NON),
            self.create_mandat(membre_reseau_elus=Person.MEMBRE_RESEAU_EXCLUS),
        ]
        s = Segment.objects.create(newsletters=[], elu=Segment.ELUS_REFERENCE)
        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_elu_ELUS_SAUF_EXCLUS_segment(self):
        includes = [
            self.create_mandat(membre_reseau_elus=Person.MEMBRE_RESEAU_OUI),
            self.create_mandat(membre_reseau_elus=Person.MEMBRE_RESEAU_NON),
        ]
        excludes = [
            self.unelected_person,
            self.create_mandat(membre_reseau_elus=Person.MEMBRE_RESEAU_EXCLUS),
        ]
        s = Segment.objects.create(newsletters=[], elu=Segment.ELUS_SAUF_EXCLUS)
        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)

    def test_elu_status_segment(self):
        includes = [
            self.create_mandat(
                membre_reseau_elus=Person.MEMBRE_RESEAU_OUI,
                statut=StatutMandat.CONFIRME,
            )
        ]
        excludes = [
            self.unelected_person,
            self.create_mandat(
                membre_reseau_elus=Person.MEMBRE_RESEAU_OUI,
                statut=StatutMandat.IMPORT_AUTOMATIQUE,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            elu=Segment.ELUS_MEMBRE_RESEAU,
            elu_status=StatutMandat.CONFIRME,
        )
        subs = s.get_people()
        for person in includes:
            self.assertIn(person, subs)
        for person in excludes:
            self.assertNotIn(person, subs)
