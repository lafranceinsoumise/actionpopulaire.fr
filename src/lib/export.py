from io import StringIO
from itertools import chain
import csv


def dicts_to_csv_lines(iterator, fieldnames):
    buffer = StringIO()
    w = csv.DictWriter(buffer, fieldnames=fieldnames)

    for d in chain(({f: f for f in fieldnames},), iterator):
        chars = w.writerow(d)
        buffer.seek(0)

        while chars:
            content = buffer.read(chars)
            chars -= len(content)
            yield content

        buffer.seek(0)
