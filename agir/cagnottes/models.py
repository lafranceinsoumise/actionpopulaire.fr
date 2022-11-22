from django.db import models

from agir.lib.models import DescriptionField


class Cagnotte(models.Model):
    nom = models.CharField(
        max_length=100,
        help_text="Utilisé notamment dans le profil sur la page des dons d'une personne.",
    )
    slug = models.SlugField(help_text="Utilisé dans l'URL pour cette cagnotte")
    public = models.BooleanField(null=False, default=True)
    titre = models.CharField(
        max_length=100,
        help_text="Utilisée en titre principal de la page de dons elle-même.",
    )
    legal = DescriptionField(
        blank=True,
        help_text="Texte additionnel à indiquer en haut de la colonne de texte légal sur la page de dons.",
    )
    description = DescriptionField(
        blank=True,
        help_text="Texte affiché dans le profil sur la page des dons d'une personne.",
    )

    url_remerciement = models.URLField(
        "URL de présentation",
        help_text="L'URL vers laquelle rediriger après le paiement.",
        blank=False,
    )
