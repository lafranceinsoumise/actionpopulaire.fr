import csv
import re
from io import StringIO
from itertools import chain


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


def snakecase_to_camelcase(identifier):
    components = identifier.split("_")
    return components[0] + "".join(word.title() for word in components[1:])


def camelcase_to_snakecase(identifier):
    identifier = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", identifier)
    identifier = re.sub("__([A-Z])", r"_\1", identifier)
    identifier = re.sub("([a-z0-9])([A-Z])", r"\1_\2", identifier)
    return identifier.lower()


def dict_to_camelcase(dictionary):
    return {snakecase_to_camelcase(k): v for k, v in dictionary.items()}


def dict_to_snakecase(dictionary):
    return {camelcase_to_snakecase(k): v for k, v in dictionary.items()}
