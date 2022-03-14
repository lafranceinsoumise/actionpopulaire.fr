import dynamic_filenames
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

from .common import ModeleGestionMixin, Compte
from ..virements import Partie, generer_fichier_virement
from ...lib.models import TimeStampedModel


class OrdreVirement(ModeleGestionMixin, TimeStampedModel):
    class Statut(models.TextChoices):
        EMIS = "E", "Émis"
        TRANSMIS = "T", "Transmis à la banque"

    statut = models.CharField(
        verbose_name="Statut", max_length=1, choices=Statut.choices, default=Statut.EMIS
    )

    # on utilise default plutôt que auto_created parce qu'on veut pouvoir mettre une date dans le futur
    date = models.DateField(
        verbose_name="Date d'exécution de l'ordre", default=timezone.now, editable=False
    )

    fichier = models.FileField(
        verbose_name="Fichier SEPA de l'ordre de virement",
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="gestion/ordres/{uuid:.2base32}/{uuid}{ext}"
        ),
        editable=False,
    )

    search_config = (("numero", "B"),)

    def __str__(self):
        from django.utils.formats import date_format

        return (
            f"Ordre de virement {date_format(self.date)} — {self.get_statut_display()}"
        )

    def generer_fichier_virement(self, force=False):
        if self.fichier and not force:
            raise ValueError("Le fichier a déjà été généré pour cet ordre.")

        reglements = list(
            self.reglements.order_by("id").select_related("depense__compte")
        )

        if not reglements:
            raise ValueError("Cet ordre de virement n'a pas de règlement lié.")

        comptes = {r.depense.compte for r in reglements}
        if len(comptes) > 1:
            raise ValueError(
                "Les règlements impliqués dans cet ordre de virement concernent plusieurs comptes différents. Cela ne "
                "devrait pas être possible !"
            )

        self.date = timezone.now().date()

        compte_emetteur: Compte = reglements[0].depense.compte

        if not compte_emetteur.emetteur_iban or not compte_emetteur.emetteur_bic:
            raise ValueError(
                "Impossible de générer un fichier de virement tant que IBAN et BIC n'ont pas été renseignés pour le"
                " compte émetteur."
            )

        # noinspection PyTypeChecker
        emetteur = Partie(
            nom=compte_emetteur.emetteur_designation,
            iban=compte_emetteur.emetteur_iban,
            bic=compte_emetteur.emetteur_bic,
        )

        virements = [
            r.generer_virement(self.date) for r in self.reglements.order_by("id")
        ]

        content = generer_fichier_virement(
            emetteur=emetteur,
            virements=virements,
            batch=False,
            check=True,
        )

        self.fichier = ContentFile(
            content,
            name=self._meta.get_field("fichier").generate_filename(
                self, f"ordre_virement_{self.id}.xml"
            ),
        )

        self.save(update_fields=["date", "fichier"])
