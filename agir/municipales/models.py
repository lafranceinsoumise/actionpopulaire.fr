from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.gis.db.models.functions import Envelope
from django.db import models
from django.db.models import UniqueConstraint


class CommunePage(models.Model):
    code = models.CharField("Code INSEE", max_length=5, editable=False)
    code_departement = models.CharField(
        "Code département", max_length=3, editable=False
    )
    coordinates = MultiPolygonField("Périmètre de la commune", geography=True)
    name = models.CharField("Nom de la commune", max_length=255)
    slug = models.SlugField("Slug")

    class Meta:
        constraints = (
            UniqueConstraint(fields=["code_departement", "slug"], name="dep_slug"),
        )
