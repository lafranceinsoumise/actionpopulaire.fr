import datetime

import reversion
from django.contrib.postgres.fields import ArrayField
from django.db import models

DELEGATIONS_CHOICES = (
    ("social", "Action sociale"),
    ("civiles juridiques", "Affaires civiles et juridiques"),
    ("économie", "Affaires économiques"),
    ("école", "Affaires scolaires"),
    ("agriculture", "Agriculture"),
    ("veterans", "Anciens combattants"),
    ("cantines", "Cantines"),
    ("commerce", "Commerce"),
    ("cimetières", "Cimetières"),
    ("international", "Coopération internationale"),
    ("culture", "Culture"),
    ("eau", "Eau assainissement"),
    ("égalité F/H", "Égalité F/H"),
    ("emploi", "Emploi"),
    ("environnement", "Environnement"),
    ("finances", "Finances"),
    ("handicap", "Handicap"),
    ("jeunesse", "Jeunesse"),
    ("logement", "Logement"),
    ("personnel", "Personnel"),
    ("discriminations", "Luttes contre discriminations"),
    ("personnes agées", "Personnes âgées"),
    ("petite enfance", "Petite enfance"),
    ("propreté", "Propreté"),
    ("santé", "Santé"),
    ("sécurité", "Sécurité"),
    ("sport", "Sport"),
    ("tourisme", "Tourisme"),
    ("déchets", "Traitement des déchets"),
    ("transport", "Transport"),
    ("travaux", "Travaux"),
    ("urbanisme", "Urbanisme"),
    ("associations", "Vie associative"),
    ("voirie", "Voirie"),
)


@reversion.register()
class MandatMunicipal(models.Model):
    MANDAT_CONSEILLER_MAJORITE = "MAJ"
    MANDAT_CONSEILLER_OPPOSITION = "OPP"
    MANDAT_MAIRE = "MAI"
    MANDAT_MAIRE_ADJOINT = "ADJ"
    MANDAT_MAIRE_DA = "MDA"

    MANDAT_CHOICES = (
        (MANDAT_CONSEILLER_MAJORITE, "Conseiller⋅e municipal de la majorité"),
        (MANDAT_CONSEILLER_OPPOSITION, "Conseiller⋅e municipal de l'opposition"),
        (MANDAT_MAIRE, "Maire"),
        (MANDAT_MAIRE_ADJOINT, "Adjoint⋅e au maire"),
        (MANDAT_MAIRE_DA, "Maire d'une commune déléguée ou associée"),
    )

    person = models.ForeignKey("people.Person", on_delete=models.CASCADE)
    commune = models.ForeignKey(
        "data_france.Commune", null=False, on_delete=models.CASCADE
    )

    debut = models.DateField(
        "Date de début du mandat", default=datetime.date(2020, 3, 22)
    )
    fin = models.DateField(
        "Date de fin du mandat",
        help_text="Date légale si dans le future, date effective si dans le passé.",
        default=datetime.date(2026, 3, 1),
    )

    mandat = models.CharField("Type de mandat", max_length=3, choices=MANDAT_CHOICES)

    email_officiel = models.ForeignKey(
        to="people.PersonEmail",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Adresse email officielle",
        help_text="L'adresse avec laquelle contacter l'élu pour des questions officielles",
    )

    delegations_municipales = ArrayField(
        verbose_name="Délégations",
        base_field=models.CharField(max_length=20, choices=DELEGATIONS_CHOICES),
        null=False,
        blank=True,
        default=list,
    )
    communautaire = models.BooleanField("Élu dans l'intercommunalité", default=False)

    class Meta:
        verbose_name_plural = "Mandats municipaux"
