import dataclasses
import re
from typing import Any, Optional

import gspread
from django.conf import settings
from django.core.exceptions import ValidationError
from gspread.utils import ValueInputOption, rowcol_to_a1


GOOGLE_SHEET_REGEX = r"^https://docs.google.com/spreadsheets/d/(?P<sid>[A-Za-z0-9_-]{40,})/.*[?#&]gid=(?P<gid>[0-9]+)"
MAX_CHUNK_SIZE = 100_000


@dataclasses.dataclass
class GoogleSheetId:
    sid: str
    gid: int


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


def check_sheet_permissions(sheet: GoogleSheetId):
    gc = gspread.service_account(settings.GCE_KEY_FILE)
    try:
        spreadsheet = gc.open_by_key(sheet.sid)
    except gspread.exceptions.APIError as e:
        if e.args[0]["code"] == 404:
            raise ValidationError("Cette spreadsheet n'existe pas.")
        elif e.args[0]["code"] == 403:
            raise ValidationError("Donnez l'accès à cette spreadsheet.")
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


def copy_array_to_sheet(sheet_id: GoogleSheetId, headers, values):
    num_rows = len(values) + 1
    num_cols = len(headers)

    sheet = open_sheet(sheet_id)
    sheet.resize(rows=num_rows, cols=num_cols)

    chunk_height = MAX_CHUNK_SIZE // num_cols

    values = [headers, *values]

    for i, rows in enumerate(grouper(values, chunk_height)):
        first_cell = rowcol_to_a1(i * chunk_height + 1, 1)
        last_cell = rowcol_to_a1((i + 1) * chunk_height, num_cols)
        sheet.batch_update(
            [{"range": f"{first_cell}:{last_cell}", "values": rows}],
            value_input_option=ValueInputOption.raw,
        )


def add_row_to_sheet(sheet_id: GoogleSheetId, values: dict[str, Any]):
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

    insert = [
        values[headers_map[i]] if i in headers_map else None
        for i in range(len(sheet_headers) + len(missing_columns))
    ]

    sheet.append_row(
        insert,
        value_input_option=ValueInputOption.raw,
        insert_data_option="INSERT_ROWS",
        table_range="A1",
    )
