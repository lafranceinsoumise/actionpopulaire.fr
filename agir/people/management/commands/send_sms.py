import re
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceMeasure
from django.core.management.base import BaseCommand, CommandError
from phonenumbers import number_type, PhoneNumberType
from tqdm import tqdm

from agir.events.models import Event
from agir.lib import data
from agir.lib.sms import send_sms, SMSSendException, compute_sms_length_information
from agir.people.models import Person


def distance_argument(d):
    m = re.match("^([0-9.]+)([a-zA-Z]+)$", d)

    if not m:
        raise ValueError(f"{d} n'est pas une mesure de distance correcte")

    return DistanceMeasure(**{m.group(2): float(m.group(1))})


def event_argument(event_id):
    try:
        return Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise ValueError("Cet événement n'existe pas.")


def coordinates_argument(coords):
    lon, lat = map(str.strip, coords.split(","))
    return Point(lon, lat, srid=4326)


def drop_duplicate_numbers(it, n=None):
    s = set()

    for number, distance in it:
        if number not in s:
            s.add(number)
            yield number, distance

        if n and len(s) >= n:
            return


def departement_argument(dep):
    return data.filtre_departement(dep)


def region_argument(reg):
    return data.filtre_region(reg)


class Command(BaseCommand):
    help = "\n".join(
        map(
            str.strip,
            """
        Permet d'envoyer un SMS à un certain nombre de personnes. Pour envoyer un SMS, vous devez sélectionner :
            - L'option -e pour indiquer l'ID d'un événement, puis -n ou -d pour le nombre de personnes, ou la distance
            - l'option -D puis le code à deux chiffres du département
            - l'option -R puis le code à deux chiffres ou le nom de la région
            - l'option -c puis les coordonnées géographiques lon,lat avec -n ou -d pour indiquer nombre ou distance
    """.splitlines(),
        )
    )

    def add_arguments(self, parser):
        parser.add_argument("-e", "--event", type=event_argument)
        parser.add_argument("-c", "--coordinates", type=coordinates_argument)
        parser.add_argument("-n", "--number", type=int)
        parser.add_argument("-d", "--distance", type=distance_argument)
        parser.add_argument("-D", "--departement", type=departement_argument)
        parser.add_argument("-R", "--region", type=region_argument)

    def can_send(self, phone):
        return phone.is_valid() and number_type(phone) in [
            PhoneNumberType.MOBILE,
            PhoneNumberType.FIXED_LINE_OR_MOBILE,
        ]

    def handle(self, event, coordinates, number, distance, departement, region):
        if (
            sum(
                0 if arg is None else 1
                for arg in [event, coordinates, departement, region]
            )
            != 1
        ):
            raise CommandError(
                "Vous devez indiquer soit un événemnet, soit des coordonnées, soit un département ou une région."
            )

        if (event or coordinates) and number is None and distance is None:
            raise CommandError(
                "Vous devez indiquer soit un nombre de personnes, soit une distance max."
            )

        if event:
            if event.coordinates is None:
                raise CommandError(
                    "Cet événement n'a pas de coordonnées géographiques."
                )

            coordinates = event.coordinates

            print(f"Évènement : {event.name}")
            print(event.short_location())
            print(event.start_time)
            print()

        print("Entrez votre message (deux lignes vides pour terminer)")

        message = ""
        last_line = None
        while True:
            current_line = input("")
            message += "\n" + current_line
            if current_line == "" and last_line == "":
                break
            last_line = current_line

        message = message.strip()

        print("Message enregistré")
        sms_info = compute_sms_length_information(message)
        print(
            f"Encodé en {sms_info.encoding}, {len(message)} caractères, {sms_info.byte_length} octets pour un total de"
            f" {sms_info.messages} SMS."
        )

        if coordinates:
            ps = (
                Person.objects.filter(subscribed_sms=True)
                .exclude(contact_phone="")
                .annotate(distance=DistanceFunction("coordinates", coordinates))
                .order_by("distance")
            )

            if distance is not None:
                ps = ps.filter(distance__lte=distance)

            res = list(
                drop_duplicate_numbers(
                    (
                        (p.contact_phone, p.distance)
                        for p in ps.iterator()
                        if self.can_send(p.contact_phone)
                    ),
                    number,
                )
            )

            numbers = [n for n, _ in res]
            max_distance = res[-1][1]
            print(f"Distance maximale : {max_distance}")

        else:
            ps = Person.objects.filter(
                region or departement, subscribed_sms=True
            ).exclude(contact_phone="")
            numbers = set(
                p.contact_phone for p in ps.iterator() if self.can_send(p.contact_phone)
            )

        print(f"Nombre de numéros : {len(numbers)}")

        print("")
        print("Prêt pour envoi.")

        answer = ""
        while answer not in ["ENVOYER", "ANNULER"]:
            answer = input("Indiquer ENVOYER ou ANNULER : ")

        if answer == "ANNULER":
            return

        excs = []

        for number in tqdm(numbers):
            try:
                send_sms(message, number)
            except SMSSendException as e:
                excs.append((number, e))

        print(f"{len(numbers) - len(excs)} SMS envoyés")

        if excs:
            print(f"{len(excs)} erreurs")

            for number, exc in excs:
                print(f"Lors de l'envoi à {number.as_e164}")
                print(repr(exc) + "\n")
