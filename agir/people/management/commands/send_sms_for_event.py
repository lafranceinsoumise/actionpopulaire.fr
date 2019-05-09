import re
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.contrib.gis.measure import Distance as DistanceMeasure
from django.core.management.base import BaseCommand, CommandError
from phonenumbers import number_type, PhoneNumberType
from tqdm import tqdm

from agir.events.models import Event
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


def drop_duplicate_numbers(it, n=None):
    s = set()

    for number, distance in it:
        if number not in s:
            s.add(number)
            yield number, distance

        if n and len(s) >= n:
            return


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("event", type=event_argument)
        parser.add_argument("-n", "--number", type=int)
        parser.add_argument("-d", "--distance", type=distance_argument)

    def can_send(self, phone):
        return phone.is_valid() and number_type(phone) in [
            PhoneNumberType.MOBILE,
            PhoneNumberType.FIXED_LINE_OR_MOBILE,
        ]

    def handle(self, event, number, distance, **options):
        if number is None and distance is None:
            raise CommandError(
                "Vous devez indiquer soit un nombre de personnes, soit une distance max."
            )

        if event.coordinates is None:
            raise CommandError("Cet événement n'a pas de coordonnées géographiques.")

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

        ps = (
            Person.objects.filter(subscribed=True)
            .exclude(contact_phone="")
            .annotate(distance=DistanceFunction("coordinates", event.coordinates))
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

        print(f"Nombre de numéros : {len(numbers)}")
        print(f"Distance maximale : {max_distance}")

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
