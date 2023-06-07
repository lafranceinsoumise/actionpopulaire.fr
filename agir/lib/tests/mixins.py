import uuid
from datetime import timedelta
import random

from django.contrib.gis.geos import Point
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

from data_france.models import Commune
from faker import Faker

from agir.lib.models import LocationMixin
from agir.events.models import Calendar, Event, OrganizerConfig, RSVP, EventSubtype
from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.people.models import Person, PersonForm, PersonFormSubmission
from agir.activity.models import Activity, Announcement


PASSWORD = "incredible password"

LOREM_IPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore
et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
"""

fake = Faker("fr_FR")


def get_random_object(model, nullable=False):
    items = model.objects.all()
    item = random.choice(items)

    if nullable == False:
        return item

    return random.choice([item, None])


# COMMONS
def create_image_url(nullable=False):
    image = "https://dummyimage.com/600x400/%s/fff&text=%s" % (
        fake.color(luminosity="dark").replace("#", ""),
        fake.word(),
    )

    if nullable == False:
        return image

    return random.choice([image, None])


def create_location():
    address = fake.street_address()
    coords = fake.local_latlng(country_code="FR", coords_only=True)
    return {
        "coordinates_type": LocationMixin.COORDINATES_EXACT,
        "coordinates": Point(float(coords[1]), float(coords[0])),
        "location_name": address,
        "location_address1": address,
        "location_address2": "App. %s" % fake.building_number(),
        "location_city": fake.city(),
        "location_zip": fake.postcode(),
        "location_state": "France",
        "location_country": "FR",
    }


# PEOPLE
def create_person():
    person = {
        "password": PASSWORD,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "contact_phone": "+33600000000",
        "gender": random.choice(
            [
                Person.GENDER_FEMALE,
                Person.GENDER_MALE,
                Person.GENDER_OTHER,
            ]
        ),
        "date_of_birth": fake.date_between(start_date="-100y"),
        "is_political_support": fake.boolean(),
        "newsletters": random.sample(
            [
                Person.NEWSLETTER_LFI,
                Person.NEWSLETTER_2022,
                Person.NEWSLETTER_2022_EN_LIGNE,
                Person.NEWSLETTER_2022_CHEZ_MOI,
                Person.NEWSLETTER_2022_PROGRAMME,
            ],
            k=random.randint(1, 5),
        ),
        "subscribed_sms": fake.boolean(),
        "event_notifications": fake.boolean(),
        "group_notifications": fake.boolean(),
        "draw_participation": fake.boolean(),
        **create_location(),
    }
    person = Person.objects.create_person(**person)
    return person


@transaction.atomic
def create_people(how_many=2):
    people = [create_person() for _ in range(how_many)]
    return people


# ACTIVITIES
def create_activity(person_email):
    person = get_random_object(Person)
    if person_email:
        try:
            person = Person.objects.get(email=person_email)
        except:
            person = person

    type = random.choice(Activity.DISPLAYED_TYPES)
    announcement = None
    if type == Activity.TYPE_ANNOUNCEMENT:
        announcement = get_random_object(Announcement)

    activity = {
        "type": type,
        "status": random.choice(
            [
                Activity.STATUS_UNDISPLAYED,
                Activity.STATUS_DISPLAYED,
                Activity.STATUS_INTERACTED,
            ]
        ),
        "event": get_random_object(Event),
        "recipient": person,
        "individual": get_random_object(Person),
        "supportgroup": get_random_object(SupportGroup),
        "announcement": announcement,
    }
    activity = Activity.objects.create(**activity)

    return activity


@transaction.atomic
def create_activities(how_many=2, person_email=None):
    activities = [create_activity(person_email) for _ in range(how_many)]
    return activities


# GROUPS
def create_group():
    contact = get_random_object(Person)
    group = {
        "name": fake.company(),
        "type": random.choice(
            [
                SupportGroup.TYPE_LOCAL_GROUP,
                SupportGroup.TYPE_THEMATIC,
                SupportGroup.TYPE_FUNCTIONAL,
            ]
        ),
        "description": fake.paragraph(),
        "image": create_image_url(True),
        "published": fake.boolean(),
        "allow_html": fake.boolean(),
        "contact_name": contact.first_name,
        "contact_email": contact.email,
        "contact_phone": contact.contact_phone,
        "contact_hide_phone": fake.boolean(),
        **create_location(),
    }
    group = SupportGroup.objects.create(**group)

    group_subtype = get_random_object(SupportGroupSubtype)
    group_subtype.supportgroups.set([group])

    nb_people = random.choice(range(20))
    for _ in range(nb_people):
        person = get_random_object(Person)
        if not Membership.objects.filter(supportgroup=group, person=person).exists():
            Membership.objects.get_or_create(
                supportgroup=group,
                person=person,
                membership_type=random.choice(
                    [
                        Membership.MEMBERSHIP_TYPE_FOLLOWER,
                        Membership.MEMBERSHIP_TYPE_MEMBER,
                        Membership.MEMBERSHIP_TYPE_MANAGER,
                        Membership.MEMBERSHIP_TYPE_REFERENT,
                    ]
                ),
            )
    return group


@transaction.atomic
def create_groups(how_many=2):
    groups = [create_group() for _ in range(how_many)]
    return groups


@transaction.atomic
def create_membership(
    supportgroup=None, person=None, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
):
    if supportgroup is None:
        supportgroup = create_group()
    if person is None:
        person = Person.objects.create_person(email=fake.email(), create_role=True)
    return Membership.objects.create(
        supportgroup=supportgroup, person=person, membership_type=membership_type
    )


# EVENTS
def create_event():
    organizer = get_random_object(Person)
    as_group = get_random_object(SupportGroup, nullable=True)
    is_upcoming = fake.boolean(chance_of_getting_true=75)
    start_time = timezone.now() + timedelta(days=random.randint(1, 30))
    report_content = ""

    if is_upcoming == False:
        start_time = timezone.now() - timedelta(days=random.randint(1, 30))
        report_content = fake.paragraph(nb_sentences=20)

    event = {
        "name": fake.paragraph(nb_sentences=1),
        "start_time": start_time,
        "end_time": start_time + timedelta(hours=3),
        "visibility": random.choice(
            [
                Event.VISIBILITY_ADMIN,
                Event.VISIBILITY_ORGANIZER,
                Event.VISIBILITY_PUBLIC,
            ]
        ),
        "report_content": report_content,
        **create_location(),
    }

    event = Event.objects.create(**event)
    OrganizerConfig.objects.create(
        event=event, person=organizer, is_creator=True, as_group=as_group
    )

    nb_people = random.choice(range(20))
    for _ in range(nb_people):
        person = get_random_object(Person)
        RSVP.objects.get_or_create(person=person, event=event)

    return event


def create_calendar(events):
    calendar = {
        "name": "Événements automatiques",
        "slug": "calendar-%s" % fake.slug(),
        "image": create_image_url(nullable=True),
        "user_contributed": fake.boolean(),
        "description": fake.paragraph(nb_sentences=15),
    }
    calendar = Calendar.objects.create(**calendar)
    calendar.events.set(events)

    return calendar


@transaction.atomic
def create_events(how_many=2):
    events = [create_event() for _ in range(how_many)]
    create_calendar(events)

    return events


# PERSON FORMS
def create_person_form():
    choices = fake.words(7)
    person_form = {
        "title": fake.paragraph(nb_sentences=1),
        "slug": "person-form-%s" % fake.slug(),
        "description": fake.paragraph(),
        "confirmation_note": fake.paragraph(),
        "main_question": "%s ?" % fake.paragraph(nb_sentences=1),
        "published": fake.boolean(),
        "editable": fake.boolean(),
        "allow_anonymous": fake.boolean(),
        "send_confirmation": fake.boolean(),
        "custom_fields": [
            {
                "title": "Questions",
                "fields": [
                    {
                        "id": "short_text",
                        "type": "short_text",
                        "label": "Short text Field",
                    },
                    {
                        "id": "long_text",
                        "type": "long_text",
                        "label": "Long text Field",
                    },
                    {
                        "id": "choice",
                        "type": "choice",
                        "label": "Choice Field",
                        "choices": choices,
                    },
                    {
                        "id": "radio_choice",
                        "type": "radio_choice",
                        "label": "Radio choice Field",
                        "choices": choices,
                    },
                    {
                        "id": "autocomplete_choice",
                        "type": "autocomplete_choice",
                        "label": "Autocomplete choice Field",
                        "choices": choices,
                    },
                    {
                        "id": "autocomplete_multiple_choice",
                        "type": "autocomplete_multiple_choice",
                        "label": "Autocomplete multiple choice Field",
                        "choices": choices,
                    },
                    {
                        "id": "multiple_choice",
                        "type": "multiple_choice",
                        "label": "Multiple choice Field",
                        "choices": choices,
                    },
                    {
                        "id": "email_address",
                        "type": "email_address",
                        "label": "Email address Field",
                    },
                    {
                        "id": "phone_number",
                        "type": "phone_number",
                        "label": "Phone number Field",
                    },
                    {"id": "url", "type": "url", "label": "Url Field"},
                    {"id": "boolean", "type": "boolean", "label": "Boolean Field"},
                    {"id": "integer", "type": "integer", "label": "Integer Field"},
                    {"id": "decimal", "type": "decimal", "label": "Decimal Field"},
                    {"id": "datetime", "type": "datetime", "label": "Datetime Field"},
                    {"id": "person", "type": "person", "label": "Person Field"},
                    {"id": "iban", "type": "iban", "label": "Iban Field"},
                    {"id": "commune", "type": "commune", "label": "Commune Field"},
                    {"id": "group", "type": "group", "label": "Group Field"},
                ],
            }
        ],
    }

    person_form = PersonForm.objects.create(**person_form)

    nb_people = random.choice(range(20))
    for _ in range(nb_people):
        person = get_random_object(Person)
        PersonFormSubmission.objects.get_or_create(
            person=person,
            form=person_form,
            data={
                "short_text": fake.words(),
                "long_text": fake.paragraph(),
                "choice": random.choice(choices),
                "radio_choice": random.choice(choices),
                "autocomplete_choice": random.choice(choices),
                "autocomplete_multiple_choice": random.choice(choices),
                "multiple_choice": random.choice(choices),
                "email_address": fake.email(),
                "phone_number": "+33600000000",
                "url": fake.url(),
                "boolean": fake.boolean(),
                "integer": random.randint(0, 100),
                "decimal": random.random(),
                "datetime": fake.date_time(),
                "person": get_random_object(Person).pk,
                "iban": fake.iban(),
                "commune": get_random_object(Commune).pk,
                "group": get_random_object(SupportGroup).pk,
            },
        )

    return person_form


@transaction.atomic
def create_person_forms(how_many=2):
    person_forms = [create_person_form() for _ in range(how_many)]

    return person_forms


@transaction.atomic
def update_fake_data():
    people = {
        "admin": Person.objects.get(email="admin@example.com"),
        "user1": Person.objects.get(email="user1@example.com"),
        "user2": Person.objects.get(email="user2@example.com"),
    }

    # Groups
    groups_subtypes = {
        "local_group_default": SupportGroupSubtype.objects.get(label="groupe local"),
        "certified_local_group": SupportGroupSubtype.objects.get(label="certifié"),
        "booklet_redaction": SupportGroupSubtype.objects.get(
            label="rédaction du livret"
        ),
        "test_thematic_booklet": SupportGroupSubtype.objects.get(label="livret test"),
    }
    groups = {
        "user1_group": SupportGroup.objects.get(name="Groupe géré par user1"),
        "user2_group": SupportGroup.objects.get(name="Groupe géré par user2"),
    }
    thematic_groups = {
        "thematic_booklet": SupportGroup.objects.get(name="Livret thématique fictif"),
        "thematic_group": SupportGroup.objects.get(
            name="Groupe thématique rattaché au livret"
        ),
    }

    # Events
    calendars = {
        "evenements_locaux": Calendar.objects.get(slug="calendar"),
        "national": Calendar.objects.get(slug="national"),
    }
    events = {
        "user1_event1": Event.objects.get(name="Événement créé par user1"),
        "user1_event2": Event.objects.get(
            name="Autre événement créé par user1 sans personne dedans"
        ),
        "user1_past_event": Event.objects.get(name="Événement passé créé par user1"),
        "user1_unpublished_event": Event.objects.get(
            name="Événement non publié créé par user1"
        ),
    }

    events["user1_event1"].start_time = timezone.now() + timedelta(days=1)
    events["user1_event1"].end_time = timezone.now() + timedelta(days=1, hours=1)
    events["user1_event1"].save()

    events["user1_event2"].start_time = timezone.now() + timedelta(days=1)
    events["user1_event2"].end_time = timezone.now() + timedelta(days=1, hours=1)
    events["user1_event2"].save()

    events["user1_past_event"].start_time = timezone.now() + timedelta(days=-1)
    events["user1_past_event"].end_time = timezone.now() + timedelta(days=-1, hours=1)
    events["user1_past_event"].save()

    events["user1_unpublished_event"].start_time = timezone.now() + timedelta(days=1)
    events["user1_unpublished_event"].end_time = timezone.now() + timedelta(
        days=1, hours=1
    )
    events["user1_unpublished_event"].save()

    # Person form
    person_form = PersonForm.objects.get(title="Formulaire")

    return {
        "people": people,
        "groups": groups,
        "events": events,
        "calendars": calendars,
        "thematic_groups": thematic_groups,
        "group_subtypes": groups_subtypes,
        "person_form": person_form,
    }


@transaction.atomic
def load_fake_data():
    people = {
        "admin": Person.objects.create_superperson("admin@example.com", PASSWORD),
        "user1": Person.objects.create_insoumise("user1@example.com", PASSWORD),
        "user2": Person.objects.create_insoumise("user2@example.com", PASSWORD),
    }

    # Groups
    groups_subtypes = {
        "local_group_default": SupportGroupSubtype.objects.get_or_create(
            label="groupe local",
            defaults={
                "visibility": SupportGroupSubtype.VISIBILITY_ALL,
            },
        )[0],
        "certified_local_group": SupportGroupSubtype.objects.get_or_create(
            label="certifié",
            defaults={
                "visibility": SupportGroupSubtype.VISIBILITY_ALL,
            },
        )[0],
        "booklet_redaction": SupportGroupSubtype.objects.get_or_create(
            label="rédaction du livret",
            defaults={
                "visibility": SupportGroupSubtype.VISIBILITY_ALL,
            },
        )[0],
        "test_thematic_booklet": SupportGroupSubtype.objects.get_or_create(
            label="livret test",
            defaults={
                "type": "B",
                "visibility": SupportGroupSubtype.VISIBILITY_ALL,
            },
        )[0],
    }
    groups = {
        "user1_group": SupportGroup.objects.create(
            name="Groupe géré par user1",
            coordinates=Point(2.349722, 48.853056),  # ND de Paris),
        ),
        "user2_group": SupportGroup.objects.create(
            name="Groupe géré par user2",
            coordinates=Point(2.301944, 49.8944),  # ND d'Amiens
        ),
    }
    groups_subtypes["local_group_default"].supportgroups.set(groups.values())
    groups_subtypes["certified_local_group"].supportgroups.set([groups["user1_group"]])
    Membership.objects.create(
        supportgroup=groups["user1_group"],
        person=people["user1"],
        membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
    )
    Membership.objects.create(
        supportgroup=groups["user2_group"],
        person=people["user2"],
        membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
    )
    Membership.objects.create(
        supportgroup=groups["user1_group"],
        person=people["user2"],
        membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
    )
    thematic_groups = {
        "thematic_booklet": SupportGroup.objects.create(
            name="Livret thématique fictif", type="B"
        ),
        "thematic_group": SupportGroup.objects.create(
            name="Groupe thématique rattaché au livret", type="B"
        ),
    }
    groups_subtypes["test_thematic_booklet"].supportgroups.set(thematic_groups.values())
    groups_subtypes["booklet_redaction"].supportgroups.set(
        [thematic_groups["thematic_booklet"]]
    )

    # Events
    calendars = {
        "evenements_locaux": Calendar.objects.create_calendar(
            "Événements locaux", slug="calendar", user_contributed=True
        ),
        "national": Calendar.objects.create_calendar("National", slug="national"),
    }

    if not EventSubtype.objects.filter(type=EventSubtype.TYPE_PUBLIC_ACTION).exists():
        EventSubtype.objects.create(
            label=uuid.uuid4().hex, type=EventSubtype.TYPE_PUBLIC_ACTION
        )

    events = {
        "user1_event1": Event.objects.create(
            name="Événement créé par user1",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            coordinates=Point(5.36472, 43.30028),  # Saint-Marie-Majeure de Marseille
        ),
        "user1_event2": Event.objects.create(
            name="Autre événement créé par user1 sans personne dedans",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            coordinates=Point(2.301944, 49.8944),  # ND d'Amiens
        ),
        "user1_past_event": Event.objects.create(
            name="Événement passé créé par user1",
            start_time=timezone.now() + timedelta(days=-1),
            end_time=timezone.now() + timedelta(days=-1, hours=1),
            coordinates=Point(7.7779, 48.5752),  # ND de Strasbourg
            report_content=LOREM_IPSUM,
        ),
        "user1_unpublished_event": Event.objects.create(
            name="Événement non publié créé par user1",
            visibility=Event.VISIBILITY_ADMIN,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            coordinates=Point(2.294444, 48.858333),  # Tour Eiffel
        ),
    }
    [
        OrganizerConfig.objects.create(
            event=event,
            person=people["user1"],
            is_creator=True,
            as_group=groups["user1_group"],
        )
        for event in [
            events["user1_event1"],
            events["user1_event2"],
            events["user1_past_event"],
            events["user1_unpublished_event"],
        ]
    ]
    [
        RSVP.objects.create(person=user, event=events["user1_event1"])
        for user in [people["user1"], people["user2"]]
    ]
    [
        RSVP.objects.create(person=user, event=events["user1_past_event"])
        for user in [people["user1"], people["user2"]]
    ]
    [
        RSVP.objects.create(person=user, event=events["user1_unpublished_event"])
        for user in [people["user1"], people["user2"]]
    ]

    # create a person form
    person_form = PersonForm.objects.create(
        title="Formulaire",
        slug="formulaire",
        description="Ma description",
        confirmation_note="Ma note de fin",
        main_question="QUESTION PRINCIPALE",
        custom_fields=[
            {
                "title": "Questions",
                "fields": [
                    {"id": "custom-field", "type": "short_text", "label": "Mon label"}
                ],
            }
        ],
    )

    PersonFormSubmission.objects.create(
        person=people["user1"], form=person_form, data={"custom-field": "saisie 1"}
    )
    PersonFormSubmission.objects.create(
        person=people["user2"], form=person_form, data={"custom-field": "saisie 2"}
    )

    return {
        "people": people,
        "groups": groups,
        "events": events,
        "calendars": calendars,
        "thematic_groups": thematic_groups,
        "group_subtypes": groups_subtypes,
        "person_form": person_form,
    }


class FakeDataMixin(TestCase):
    def setUp(self):
        self.data = load_fake_data()

        for k, v in self.data.items():
            setattr(self, k, v)

        super().setUp()
