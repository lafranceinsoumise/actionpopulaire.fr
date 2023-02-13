from data_france.models import (
    Region,
    Departement,
    Commune,
    CodePostal,
    CollectiviteRegionale,
    CollectiviteDepartementale,
)
from data_france.utils import TypeNom
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.db import transaction


def import_communes_test_data():
    with transaction.atomic():
        reg = Region.objects.create(
            code="01",
            nom="Région",
            type_nom=TypeNom.ARTICLE_LA,
            chef_lieu_id=1,
        )
        col_reg = CollectiviteRegionale.objects.create(
            code="01R",
            nom="Région",
            type=CollectiviteRegionale.TYPE_CONSEIL_REGIONAL,
            type_nom=TypeNom.ARTICLE_LA,
            actif=True,
            region=reg,
        )
        dep = Departement.objects.create(
            code="01",
            nom="Département",
            type_nom=TypeNom.ARTICLE_LE,
            region=reg,
            chef_lieu_id=1,
        )
        col_dep = CollectiviteDepartementale.objects.create(
            code="01D",
            nom="Département",
            type=CollectiviteDepartementale.TYPE_CONSEIL_DEPARTEMENTAL,
            type_nom=TypeNom.ARTICLE_LE,
            region=reg,
            actif=True,
        )
        c1 = Commune.objects.create(
            id=1,
            code="00001",
            type=Commune.TYPE_COMMUNE,
            nom="Première",
            type_nom=TypeNom.ARTICLE_LA,
            geometry=MultiPolygon(Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))),
            departement=dep,
        )
        c2 = Commune.objects.create(
            id=2,
            code="00002",
            type=Commune.TYPE_COMMUNE,
            nom="Seconde",
            type_nom=TypeNom.ARTICLE_LA,
            geometry=MultiPolygon(Polygon(((0, 0), (0, -1), (1, -1), (1, 0), (0, 0)))),
            departement=dep,
        )
        c3 = Commune.objects.create(
            id=3,
            code="00003",
            type=Commune.TYPE_COMMUNE,
            nom="Troisième",
            type_nom=TypeNom.ARTICLE_LA,
            geometry=MultiPolygon(
                Polygon(((0, 0), (0, -1), (-1, -1), (-1, 0), (0, 0)))
            ),
            departement=dep,
        )
        arr1 = Commune.objects.create(
            id=4,
            code="10001",
            type=Commune.TYPE_ARRONDISSEMENT_PLM,
            nom="Arrondissement",
            type_nom=TypeNom.VOYELLE,
            commune_parent=c1,
            geometry=MultiPolygon(
                Polygon(((0, 0), (0, 0.5), (1, 0.5), (1, 0), (0, 0)))
            ),
        )

        cp1 = CodePostal.objects.create(code="12345")
        cp2 = CodePostal.objects.create(code="54321")
        cp3 = CodePostal.objects.create(code="12300")

        cp1.communes.set([c1])
        cp2.communes.set([c2, c3])
        cp3.communes.set([arr1])
