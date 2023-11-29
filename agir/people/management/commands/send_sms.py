import secrets
from argparse import FileType
from pathlib import Path

from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from django.core.management.base import BaseCommand, CommandError
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import number_type, PhoneNumberType
from tqdm import tqdm

from agir.lib.management_utils import (
    datetime_argument,
    distance_argument,
    event_argument,
    coordinates_argument,
    departement_argument,
    region_argument,
    segment_argument,
)
from agir.lib.sms import compute_sms_length_information, send_bulk_sms, SMSSendException
from agir.people.models import Person


def drop_duplicate_numbers(it, n=None):
    s = set()

    for number, distance in it:
        if number not in s:
            s.add(number)
            yield number, distance

        if n and len(s) >= n:
            return


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
        parser.add_argument("-S", "--segment", type=segment_argument)
        parser.add_argument("-a", "--at", type=datetime_argument)
        parser.add_argument("-T", "--exclude-telegram", action="store_true")
        parser.add_argument("-s", "--sentfile", type=FileType(mode="r"))
        parser.add_argument("-E", "--export-file", type=FileType(mode="w"))

    def can_send(self, phone):
        return (
            isinstance(phone, PhoneNumber)
            and phone.is_valid()
            and number_type(phone)
            in [
                PhoneNumberType.MOBILE,
                PhoneNumberType.FIXED_LINE_OR_MOBILE,
            ]
        )

    def write_numbers(self, path, numbers):
        with open(path, "w") as f:
            f.write("\n".join(numbers))

    def read_numbers(self, file):
        return set(PhoneNumber.from_string(n) for n in file.read().split("\n"))

    def handle(
        self,
        event,
        coordinates,
        number,
        distance,
        departement,
        region,
        segment,
        sentfile,
        at,
        exclude_telegram,
        export_file,
        **options,
    ):
        if (
            sum(
                0 if arg is None else 1
                for arg in [event, coordinates, departement, region, segment]
            )
            != 1
        ):
            raise CommandError(
                "Vous devez indiquer soit un événemnet, soit des coordonnées, soit un département, une région ou un segment."
            )

        if (event or coordinates) and number is None and distance is None:
            raise CommandError(
                "Vous devez indiquer soit un nombre de personnes, soit une distance max."
            )

        if event:  # we generate coordinates from event
            if event.coordinates is None:
                raise CommandError(
                    "Cet événement n'a pas de coordonnées géographiques."
                )

            coordinates = event.coordinates

            self.stdout.write(f"Événement : {event.name}")
            self.stdout.write(event.short_location())
            self.stdout.write(event.local_start_time.strftime("Le %d/%m/%Y à %H:%M"))
            self.stdout.write("\n")  # ligne vide

        if coordinates:  # two case : central point coordinates or any other
            ps = (
                Person.objects.filter(subscribed_sms=True)
                .exclude(contact_phone="")
                .annotate(distance=DistanceFunction("coordinates", coordinates))
                .order_by("distance")
            )

            if distance is not None:
                ps = ps.filter(distance__lte=distance)

            if exclude_telegram:
                ps = ps.exclude(meta__has_telegram=True)

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
            self.stdout.write(f"Distance maximale : {max_distance}")
        else:
            if segment:
                ps = segment.get_people().exclude(contact_phone="").distinct()
                self.stdout.write(f"Segment : {segment.name}")
            else:
                ps = Person.objects.filter(
                    region or departement, subscribed_sms=True
                ).exclude(contact_phone="")

            if exclude_telegram:
                ps = ps.exclude(meta__has_telegram=True)

            numbers = set(
                p.contact_phone for p in ps.iterator() if self.can_send(p.contact_phone)
            )

        self.stdout.write(f"Nombre de numéros : {len(numbers)}")

        if export_file is not None:
            export_file.write("\n".join(str(number) for number in numbers))
            return

        if sentfile is not None:
            sent_numbers = self.read_numbers(sentfile)
            numbers.difference_update(sent_numbers)
            self.stdout.write(
                f"{len(numbers)} après prise en compte des numéros déjà envoyés."
            )

        self.stdout.write("\n")  # empty line

        self.stdout.write("Entrez votre message (deux lignes vides pour terminer)")

        message = ""
        last_line = None
        while True:
            current_line = input("")
            message += "\n" + current_line
            if current_line == "" and last_line == "":
                break
            last_line = current_line

        message = message.strip()

        self.stdout.write("Message enregistré")
        sms_info = compute_sms_length_information(message)
        self.stdout.write(
            f"Encodé en {sms_info.encoding}, {len(message)} caractères, {sms_info.byte_length} octets pour un total de"
            f" {sms_info.messages} SMS."
        )

        self.stdout.write("")
        self.stdout.write("Prêt pour envoi.")

        answer = ""
        while answer not in ["ENVOYER", "ANNULER"]:
            answer = input("Indiquer ENVOYER ou ANNULER : ")

        if answer == "ANNULER":
            return

        token = secrets.token_urlsafe(4)
        sent_filename = Path(f"sent.{token}")
        invalid_filename = Path(f"invalid.{token}")

        try:
            sent, invalid = send_bulk_sms(message, tqdm(numbers), at=at)
        except SMSSendException as e:
            self.stderr.write("Erreur lors de l'envoi des SMS.")
            self.stderr.write(
                f"{len(e.sent)} SMS ont déjà été envoyés ({len(e.invalid)} numéros invalides)."
            )

            try:
                self.write_numbers(sent_filename, e.sent)
                self.write_numbers(invalid_filename, e.invalid)
            except OSError:
                self.stderr.write(
                    "Impossible d'écrire les fichiers avec les numéros testés."
                )
                raise

            self.stderr.write(f"Fichiers {sent_filename} et {invalid_filename} écrits.")
            return 1

        self.stdout.write(f"{len(sent)} SMS envoyés")

        if invalid:
            self.stdout.write(f"{len(invalid)} numéros invalides")
            self.write_numbers(invalid_filename, invalid)
            self.stdout.write(f"{invalid_filename} écrit.")
