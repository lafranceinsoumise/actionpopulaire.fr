import dataclasses
import re
from functools import wraps
from typing import Any, Optional

import gspread
import pandas as pd
from django.conf import settings
from django.core.exceptions import ValidationError
from gspread.utils import ValueInputOption, rowcol_to_a1, ValueRenderOption

from agir.lib.celery import retriable_task

GOOGLE_SHEET_REGEX = r"^https://docs.google.com/spreadsheets/d/(?P<sid>[A-Za-z0-9_-]{40,})/.*[?#&]gid=(?P<gid>[0-9]+)"
GOOGLE_SHEET_TEMPLATE = "https://docs.google.com/spreadsheets/d/{sid}/edit#gid={gid}"
MAX_CHUNK_SIZE = 100_000


class _TemporaryGspreadError(Exception):
    pass


def gspread_task(task):
    """Permet de retenter une tâche celery qui utilise gspread

    Nous avons constaté des problèmes de sérialisation des exceptions de gspread.
    Pour les éviter, on utilise donc une exception spécifique qui est levée en lieu et place de l'exception
    de gspread, et qui ne posera pas de problème de sérialisation.

    Pour éviter le chaînage d'exception (l'exception d'origine serait quand même sérialisée dans ce cas !), on prend
    garde à utiliser la forme raise … from None.
    :param task:
    :return:
    """

    @wraps(task)
    def _wrapped(*args, **kwargs):
        try:
            task(*args, **kwargs)
        except gspread.exceptions.APIError as e:
            raise _TemporaryGspreadError(
                *e.args,
            ) from None

    return retriable_task(_wrapped, start=5, retry_on=(_TemporaryGspreadError,))


@dataclasses.dataclass
class GoogleSheetId:
    sid: str
    gid: int

    @property
    def url(self):
        return GOOGLE_SHEET_TEMPLATE.format(gid=self.gid, sid=self.sid)

    def open(self):
        return open_sheet(self)


def grouper(array: list, n: int):
    for i in range(0, len(array), n):
        yield array[i : i + n]


def parse_sheet_link(link: str) -> Optional[GoogleSheetId]:
    m = re.match(GOOGLE_SHEET_REGEX, link)

    if not m:
        return None

    sid = m.group("sid")
    gid = int(m.group("gid"))

    return GoogleSheetId(sid, gid)


def open_sheet(sheet: GoogleSheetId):
    gc = gspread.service_account(settings.GCE_KEY_FILE)
    spreadsheet = gc.open_by_key(sheet.sid)
    sheet = spreadsheet.get_worksheet_by_id(sheet.gid)

    return sheet


def clear_sheet(sheet_id: GoogleSheetId):
    sheet = open_sheet(sheet_id)
    return sheet.clear()


def check_sheet_permissions(sheet: GoogleSheetId):
    gc = gspread.service_account(settings.GCE_KEY_FILE)

    try:
        spreadsheet = gc.open_by_key(sheet.sid)
    except PermissionError:
        raise ValidationError(
            "Action populaire n'a pas la permission de modifier la feuille Google sheet."
        )
    except gspread.exceptions.SpreadsheetNotFound:
        raise ValidationError("Cette spreadsheet n'existe pas.")
    except gspread.exceptions.APIError as e:
        if e.args[0]["code"] == 404:
            raise ValidationError("Cette spreadsheet n'existe pas.")
        elif e.args[0]["code"] == 403:
            raise ValidationError(
                "Action populaire n'a pas la permission de modifier la feuille Google sheet."
            )
        raise

    try:
        spreadsheet.list_permissions()
    except gspread.exceptions.APIError as e:
        if e.args[0]["code"] == 403:
            raise ValidationError(
                "Action populaire n'a pas la permission de modifier la feuille Google sheet."
            )
        raise

    try:
        spreadsheet.get_worksheet_by_id(sheet.gid)
    except gspread.exceptions.WorksheetNotFound:
        raise ValidationError(
            "Le tableur existe, mais la feuille n'existe pas ou plus."
        )


def copy_array_to_sheet(sheet_id: GoogleSheetId, values):
    num_rows = len(values)
    num_cols = len(values[0])

    sheet = open_sheet(sheet_id)
    sheet.resize(rows=num_rows, cols=num_cols)

    chunk_height = MAX_CHUNK_SIZE // num_cols

    results = []

    for i, rows in enumerate(grouper(values, chunk_height)):
        first_cell = rowcol_to_a1(i * chunk_height + 1, 1)
        last_cell = rowcol_to_a1((i + 1) * chunk_height, num_cols)
        result = sheet.update(
            f"{first_cell}:{last_cell}",
            rows,
            value_input_option=ValueInputOption.raw,
        )
        results.append(result)

    return results


def copy_records_to_sheet(sheet_id: GoogleSheetId, records):
    df = pd.DataFrame(records)
    datalist = [df.columns.values.tolist()] + df.values.tolist()
    return copy_array_to_sheet(sheet_id, datalist)


def add_row_to_sheet(sheet_id: GoogleSheetId, values: dict[str, Any], id_column=None):
    if id_column is not None:
        assert id_column in values
    sheet = open_sheet(sheet_id)

    sheet_headers = sheet.row_values(1)

    headers_map = {i: h for i, h in enumerate(sheet_headers) if h in values}

    # itérer les clés pour préserver l'ordre des nouvelles colonnes
    missing_columns = [h for h in values.keys() if h not in sheet_headers]

    if missing_columns:
        if sheet.col_count < len(sheet_headers) + len(missing_columns):
            sheet.resize(
                rows=sheet.row_count, cols=len(sheet_headers) + len(missing_columns)
            )

        first_new_col = len(sheet_headers) + 1
        last_new_col = len(sheet_headers) + len(missing_columns)

        headers_map.update(
            {
                i: h
                for h, i in zip(
                    missing_columns,
                    range(first_new_col - 1, last_new_col),
                )
            }
        )

        header_range = (
            f"{rowcol_to_a1(1, first_new_col)}:{rowcol_to_a1(1, last_new_col)}"
        )
        sheet.update(header_range, [missing_columns])

    # la valeur par défaut est une chaîne vide plutôt que None car sinon gspread
    # n'écrase pas une potentielle valeur existante.
    insert = [
        values[headers_map[i]] if i in headers_map else ""
        for i in range(len(sheet_headers) + len(missing_columns))
    ]

    if id_column is not None:
        id_pos = next(i for i, c in headers_map.items() if c == id_column)
        id_values = sheet.col_values(
            id_pos + 1, value_render_option=ValueRenderOption.unformatted
        )[1:]

        try:
            existing_row = id_values.index(values[id_column]) + 2
        except ValueError:
            pass
        else:
            first_cell = rowcol_to_a1(existing_row, 1)
            last_cell = rowcol_to_a1(existing_row, len(insert))
            sheet.update(f"{first_cell}:{last_cell}", [insert])
            return

    sheet.append_row(
        insert,
        value_input_option=ValueInputOption.raw,
        insert_data_option="INSERT_ROWS",
        table_range="A1",
    )
