from django.contrib.gis.db.models import MultiPolygonField
from django.db import models
from django.db.models import UniqueConstraint

from agir.lib.utils import front_url


class CommunePage(models.Model):
    code = models.CharField("Code INSEE", max_length=5, editable=False)
    code_departement = models.CharField(
        "Code département", max_length=3, editable=False
    )
    coordinates = MultiPolygonField("Périmètre de la commune", geography=True)
    name = models.CharField("Nom de la commune", max_length=255)
    slug = models.SlugField("Slug")
    twitter = models.CharField("Identifiant Twitter", max_length=255, blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.code_departement)

    def get_absolute_url(self):
        return front_url(
            "view_commune",
            kwargs={"code_departement": self.code_departement, "slug": self.slug},
        )

    class Meta:
        constraints = (
            UniqueConstraint(fields=["code_departement", "slug"], name="dep_slug"),
        )
        verbose_name = "Page de commune"
        verbose_name_plural = "Pages de commune"
