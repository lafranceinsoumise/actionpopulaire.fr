import reversion
from data_france.typologies import CSP
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import formats

from agir.lib.history import HistoryMixin
from agir.lib.models import DescriptionField
from agir.lib.utils import numero_unique


class Sexe(models.TextChoices):
    MASCULIN = "M", "Masculin"
    FEMININ = "F", "Féminin"


class TypeCandidature(models.TextChoices):
    INAPPLICABLE = "", "Inapplicable"
    TITULAIRE = "T", "Titulaire"
    SUPPLEANT = "S", "Suppléant"
    INDIFFERENT = "I", "Indifférent"


class TypeScrutin(models.TextChoices):
    LISTE_UN_TOUR = "LUT", "Scrutin de liste à un tour"
    LISTE_DEUX_TOURS = "LDT", "Scrutin de liste à deux tours"
    UNINOMINAL_DEUX_TOURS = "UDT", "Scrutin uninominal à deux tours"


class EtatCandidature(models.IntegerChoices):
    INCONNU = -50, "État inconnu"
    REJETE = -20, "Rejeté (raison à préciser)"
    INCOMPLET = -10, "Rejeté car incomplet"
    NON_RELUE = 0, "Pas encore relue"
    COMPLET = 10, "Complet"
    RETENU = 20, "Retenu pour examen"
    CHOISIE = 100, "Choisie et validée"


class AutreLieu(models.TextChoices):
    NON = ("non", "Non")
    DEPARTEMENT = (
        "département",
        "Dans le même département",
    )
    REGION = "région", "Dans la même région"


@reversion.register()
class Scrutin(HistoryMixin, models.Model):
    nom = models.CharField("Nom du scrutin", max_length=60)

    circonscription_content_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE
    )

    type_scrutin = models.CharField(
        verbose_name="Type de scrutin", max_length=10, choices=TypeScrutin.choices
    )

    date = models.DateField(
        verbose_name="Date du scrutin",
    )

    def __repr__(self):
        return f"<Scrutin: {self.nom}>"

    def __str__(self):
        return f"{self.nom} ({formats.date_format(self.date, 'SHORT_DATE_FORMAT')})"

    class Meta:
        ordering = ("-date",)


@reversion.register()
class Candidature(HistoryMixin, models.Model):
    Etat = EtatCandidature

    code = models.CharField(
        verbose_name="Code candidature",
        max_length=7,
        editable=False,
        blank=False,
        default=numero_unique,
        unique=True,
        help_text="Code unique pour identifier une candidature.",
    )

    person = models.ForeignKey(
        to="people.Person",
        on_delete=models.CASCADE,
        related_name="candidatures",
        related_query_name="candidature",
    )

    scrutin = models.ForeignKey(
        to=Scrutin,
        on_delete=models.PROTECT,
    )

    circonscription_content_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE
    )
    circonscription_object_id = models.IntegerField()

    circonscription = GenericForeignKey(
        ct_field="circonscription_content_type", fk_field="circonscription_object_id"
    )

    ailleurs = models.CharField(
        verbose_name="Accepte de candidater ailleurs",
        choices=AutreLieu.choices,
        blank=True,
        max_length=15,
    )

    date = models.DateTimeField(
        verbose_name="Date de candidature",
        null=True,
        editable=False,
        help_text="Date à laquelle la candidature a été reçue",
    )

    etat = models.IntegerField(
        verbose_name="État de cette candidature",
        null=False,
        default=EtatCandidature.NON_RELUE,
        choices=EtatCandidature.choices,
    )

    type_candidature = models.CharField(
        verbose_name="type de candidature souhaitée",
        max_length=1,
        choices=TypeCandidature.choices,
        blank=True,
    )

    nom = models.CharField(verbose_name="nom de famille", max_length=255)
    prenom = models.CharField(verbose_name="prénom", max_length=255)
    sexe = models.CharField(
        verbose_name="sexe à l'état civil", max_length=1, choices=Sexe.choices
    )

    date_naissance = models.DateField(
        "date de naissance",
    )

    code_postal = models.CharField(
        verbose_name="Code postal",
        max_length=20,
        blank=False,
    )

    ville = models.CharField(verbose_name="Ville", max_length=200, blank=False)

    categorie_socio_professionnelle = models.IntegerField(
        verbose_name="Catégorie socioprofessionnelle", choices=CSP.choices, null=True
    )

    profession_foi = DescriptionField("profession de foi")

    informations = DescriptionField(
        "informations supplémentaires",
        blank=True,
        help_text="Merci de n'indiquer que des éléments factuels.",
    )

    meta = models.JSONField(
        "autres données",
        default=dict,
        null=False,
        blank=True,
        help_text="éléments techniques supplémentaires",
    )

    def __repr__(self):
        return f"<Candidature: {self.nom}, {self.prenom} ({self.scrutin})>"

    def __str__(self):
        return f"Candidature de {self.nom}, {self.prenom}, {self.scrutin}, {self.circonscription}"


@reversion.register()
class Autorisation(models.Model):
    groupe = models.ForeignKey(
        to=Group, on_delete=models.CASCADE, null=False, blank=False
    )

    scrutin = models.ForeignKey(
        Scrutin, on_delete=models.CASCADE, null=False, blank=False
    )
    prefixes = ArrayField(
        verbose_name="préfixes",
        base_field=models.CharField(max_length=20),
        help_text="Préfixes des circonscriptions sur lesquelles portent les permissions.",
        default=list,
    )

    ecriture = models.BooleanField(verbose_name="Droits de modification", default=False)

    def __repr__(self):
        return f"<Autorisation: scrutin={self.scrutin!r} groupe={self.groupe!r} prefixes={self.prefixes!r}>"
