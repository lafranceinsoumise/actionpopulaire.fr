import dynamic_filenames
from django.db import models
from django.utils import timezone

from .common import ModeleGestionMixin
from ...lib.models import TimeStampedModel


class OrdreVirement(ModeleGestionMixin, TimeStampedModel):
    class Statut(models.TextChoices):
        EMIS = "E", "Émis"
        TRANSMIS = "T", "Transmis à la banque"
        RAPPROCHE = "R", "Rapproché"

    statut = models.CharField(
        verbose_name="Statut", max_length=1, choices=Statut.choices, default=Statut.EMIS
    )

    reglements = models.ManyToManyField(
        to="Reglement", related_name="ordre", related_query_name="ordres", blank=False
    )

    # on utilise default plutôt que auto_created parce qu'on veut pouvoir mettre une date dans le futur
    date = models.DateField(
        verbose_name="Date d'exécution de l'ordre", default=timezone.now
    )

    fichier = models.FileField(
        verbose_name="Fichier SEPA de l'ordre de virement",
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="gestion/ordres/{uuid:.2base32}/{uuid}{ext}"
        ),
    )

    search_config = (("numero", "B"),)
