from django.contrib.gis.geos import Point
from django.utils import timezone

from agir.events.models import Event, RSVP, OrganizerConfig
from agir.people.models import Person
from agir.groups.models import SupportGroup


Person.objects.create_superperson('admin@exemple.fr', 'incredible password')

st = timezone.make_aware(timezone.datetime(2018, 8, 2, 10, 30), timezone=timezone.get_default_timezone())
et = st + timezone.timedelta(hours=2)

# past events
for i in range(1,50):
    p = Person.objects.create_person(str(i) + '@exemple.fr')
    e = Event.objects.create(
        name="Événement trop cool de l'utilisateur " + str(i),
        start_time=st,
        end_time=et,
        coordinates=Point(5.3601266,43.2944724)
    )
    RSVP.objects.create(
        person=p,
        event=e
    )
    OrganizerConfig.objects.create(
        person=p,
        event=e,
        is_creator=True
    )

SupportGroup.objects.create(
    name="Groupe d'action test de Tour",
    coordinates=Point(0.6249003,47.3942462),
    contact_email="contact@exemple.fr",
    contact_name="Arthur Cheysson"
)

SupportGroup.objects.create(
    name="Groupe d'action test de Bordeaux",
    coordinates=Point(-0.6212462,44.8637834),
    contact_email="contact@exemple.fr",
    contact_name="Arthur Cheysson"
)

SupportGroup.objects.create(
    name="Groupe d'action test de Cahors",
    coordinates=Point(1.4039078,44.4565779),
    contact_email="contact@exemple.fr",
    contact_name="Arthur Cheysson"
)

Event.objects.create(
    name="Les AMFiS d'été",
    coordinates=(5.3892596, 43.2725924),
    contact_email="amfis@lafranceinsoumise.fr",
    contact_name="Arthur Cheysson",
    start_time=timezone.make_aware(timezone.datetime(2018, 8, 23, 10, 30), timezone=timezone.get_default_timezone()),
    end_time=timezone.make_aware(timezone.datetime(2018, 8, 26, 12, 30), timezone=timezone.get_default_timezone())
)
