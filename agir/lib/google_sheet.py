from typing import Any

import gspread
from django.conf import settings
from gspread.utils import ValueInputOption, rowcol_to_a1

MAX_CHUNK_SIZE = 100_000


def grouper(array: list, n: int):
    for i in range(0, len(array), n):
        yield array[i : i + n]


def open_sheet(sid: str, gid: int):
    gc = gspread.service_account(settings.GCE_KEY_FILE)
    spreadsheet = gc.open_by_key(sid)
    sheet = spreadsheet.get_worksheet_by_id(gid)

    return sheet


def copy_array_to_sheet(sid: str, gid: int, headers, values):
    num_rows = len(values) + 1
    num_cols = len(headers)

    sheet = open_sheet(sid, gid)
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


def add_row_to_sheet(sid: str, gid: int, values: dict[str, Any]):
    sheet = open_sheet(sid, gid)

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
