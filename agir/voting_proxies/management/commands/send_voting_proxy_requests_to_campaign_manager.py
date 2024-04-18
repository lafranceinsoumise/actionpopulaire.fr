import re

from django.db.models import Q, Value
from django.utils import timezone
from glom import T, glom, Coalesce
from unidecode import unidecode

from agir.lib.commands import BaseCommand
from agir.lib.data import departements_choices
from agir.lib.google_sheet import (
    GoogleSheetId,
    open_sheet,
    parse_sheet_link,
    copy_records_to_sheet,
    clear_sheet,
)
from agir.voting_proxies.models import VotingProxyRequest

INDEX_FILE_ID = "1Ugnzr77oiYtwMYZsIrGa6klq0S-G7HtLCaP1I0_qpp0"
LOG_FILE_ID = GoogleSheetId(INDEX_FILE_ID, 395114866)
TEST_SHEET_ID = GoogleSheetId(INDEX_FILE_ID, 521378227)
PRODUCTION_SHEET_ID = GoogleSheetId(INDEX_FILE_ID, 0)

DEPARTEMENT_CODE_RE = re.compile(
    r"^(?:99|[01345678][0-9]|2[1-9AB]|9(?:[0-5]|7[1-8]|8[678]))$"
)

SPEC_VPR = {
    "Commune ou consulat d'inscription": (
        Coalesce("commune.nom_complet", "consulate.nom"),
        lambda location: location.upper(),
    ),
    "Nom de famille": ("last_name", lambda name: name.upper()),
    "Prénoms": ("first_name", lambda name: name.title()),
    "E-mail": ("email", lambda name: name.lower()),
    "Téléphone": "contact_phone",
    "Bureau de vote": "polling_station_number",
    "Numéro national d'électeur": "voter_id",
    "Département d'inscription": "voting_departement",
    "Création": T.created.strftime("%d/%m/%Y"),
    "Id": "id.hex",
    "Lien d'acceptation": "reply_to_url",
}


DEPARTEMENT = {
    **dict(departements_choices),
    "99": "99 - Français établis hors de France",
}


class Command(BaseCommand):
    help = "Send pending voting proxy requests to campaign managers"
    language = "fr"

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--departements",
            dest="departements",
            default=None,
            help=f"Limiter à certains départements (code du département ou 99 pour les FE). "
            f"Ex. -d 01,02,03,99",
        )
        parser.add_argument(
            "-t",
            "--test",
            dest="test_mode",
            action="store_true",
            default=False,
            help=f"Lancer la commande en mode test",
        )
        super().add_arguments(parser)

    def get_target_files(self, departements=None, test_mode=False):
        sheet_id = TEST_SHEET_ID if test_mode else PRODUCTION_SHEET_ID
        index_sheet = open_sheet(sheet_id)
        index = index_sheet.get_all_records()
        files = {
            i["Département"].split(" - ")[0]: parse_sheet_link(i["vp_url"])
            for i in index
            if not departements or i["Département"].split(" - ")[0] in departements
        }

        return files

    def get_data(self, departement):
        voting_proxy_requests = VotingProxyRequest.objects.pending()

        if departement == "99":
            voting_proxy_requests = voting_proxy_requests.select_related(
                "consulate",
            ).filter(consulate__isnull=False)
        else:
            voting_proxy_requests = voting_proxy_requests.select_related(
                "commune",
                "commune__departement",
                "commune__commune_parent",
                "commune__commune_parent__departement",
            ).filter(
                Q(commune__departement__code=departement)
                | Q(commune__commune_parent__departement__code=departement)
            )

        voting_proxy_requests = voting_proxy_requests.annotate(
            voting_departement=Value(DEPARTEMENT[departement])
        )

        data = glom(voting_proxy_requests, [SPEC_VPR])

        data = sorted(
            data,
            key=lambda i: tuple(unidecode(i[k]) for k in tuple(SPEC_VPR.keys())[:3]),
        )

        return data

    def update_sheet(self, target_file, data):
        if self.dry_run:
            return

        if data:
            copy_records_to_sheet(target_file, data)
        else:
            clear_sheet(target_file)

    def log_result(self, result, test_mode):
        if not result:
            return

        log_data = [
            {
                "Département": DEPARTEMENT[departement],
                "Nombre": count,
                "Date": timezone.now().strftime("%d/%m/%Y %H:%M"),
                "Test": test_mode,
                "Dry-run": self.dry_run,
                "URL": target_file.url,
            }
            for (departement, target_file, count) in result
        ]

        copy_records_to_sheet(LOG_FILE_ID, log_data)

    def handle(
        self,
        *args,
        departements=None,
        test_mode=False,
        **kwargs,
    ):
        if departements:
            departements = sorted(departements.split(","))
            incorrects = [c for c in departements if not DEPARTEMENT_CODE_RE.match(c)]

            if incorrects:
                self.error(
                    f"Les code suivants sont incorrects : {','.join(incorrects)}"
                )
                return

        self.info(
            f"\nExport des données pour les départements sélectionnés : {','.join(departements)}\n"
            if departements
            else "\nExport des données pour tous les départements\n"
        )

        target_files = self.get_target_files(
            departements=departements, test_mode=test_mode
        )

        self.init_tqdm(len(target_files))

        result = []
        errors = []

        for departement, target_file in target_files.items():
            self.tqdm.update(1)
            self.log_current_item(DEPARTEMENT[departement])
            try:
                data = self.get_data(departement)
                self.update_sheet(target_file, data)
                result.append((departement, target_file, len(data)))
            except Exception as e:
                result.append((departement, target_file, -1))
                errors.append((departement, e))

        self.tqdm.close()

        self.log_result(result, test_mode=test_mode)

        for departement, e in errors:
            self.exception(f"{departement}: {e}")
