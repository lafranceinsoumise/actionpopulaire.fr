import csv

import os

with open(os.path.dirname(os.path.realpath(__file__)) + "/departements.csv") as file:
    departements = list(csv.DictReader(file))
