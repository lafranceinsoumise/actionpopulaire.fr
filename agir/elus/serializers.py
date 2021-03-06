from pathlib import PurePath

from data_france.models import EluMunicipal
from data_france.typologies import Fonction
from django.db.models import TextChoices, Q
from rest_framework import serializers

from agir.elus.models import RechercheParrainageMaire

CRITERE_INCLUSION_ELUS = Q(fonction__in=[Fonction.MAIRE, Fonction.MAIRE_DELEGUE]) | Q(
    fonction_epci=Fonction.PRESIDENT
)


class MairieSerializer(serializers.Serializer):
    adresse = serializers.CharField(source="mairie_adresse")
    accessibilite = serializers.CharField(source="mairie_accessibilite")
    detailsAccessibilite = serializers.CharField(source="mairie_accessibilite_details")
    horaires = serializers.JSONField(source="mairie_horaires")
    email = serializers.CharField(source="mairie_email")
    telephone = serializers.CharField(source="mairie_telephone")
    site = serializers.CharField(source="mairie_site")


class EluMunicipalSerializer(serializers.Serializer):
    class Statut(TextChoices):
        DISPONIBLE = "D", "Disponible"
        A_CONTACTER = "A", "À contacter"
        EN_COURS = "E", "En cours"
        TERMINE = "T", "Déjà rencontré"
        PERSONNELLEMENT_VU = "P", "Je l'ai vu"

    id = serializers.IntegerField()
    nomComplet = serializers.SerializerMethodField()
    sexe = serializers.CharField()
    titre = serializers.SerializerMethodField()
    commune = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    statut = serializers.CharField()
    idRechercheParrainage = serializers.IntegerField(
        source="recherche_parrainage_maire_id"
    )

    mairie = MairieSerializer(source="commune")

    def get_nomComplet(self, obj):
        return f"{obj.prenom} {obj.nom}"

    def get_titre(self, obj):
        return obj.libelle_fonction

    def get_commune(self, obj):
        return obj.commune.nom_complet

    def get_distance(self, obj):
        return obj.distance.km


class CreerRechercheSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    elu = serializers.PrimaryKeyRelatedField(
        queryset=EluMunicipal.objects.filter(CRITERE_INCLUSION_ELUS)
    )

    def create(self, validated_data):
        return RechercheParrainageMaire.objects.create(
            elu=self.validated_data["elu"], person=self.context["request"].user.person
        )


class ModifierRechercheSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(
        choices=[
            RechercheParrainageMaire.Statut.ENGAGEMENT,
            RechercheParrainageMaire.Statut.REFUS,
            RechercheParrainageMaire.Statut.NE_SAIT_PAS,
            RechercheParrainageMaire.Statut.AUTRE_ENGAGEMENT,
            RechercheParrainageMaire.Statut.ANNULEE,
        ]
    )

    commentaires = serializers.CharField(required=False)
    formulaire = serializers.FileField(required=False)

    def validate_formulaire(self, value):
        name = value.name
        ext = PurePath(name).suffix

        if ext.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
            raise serializers.ValidationError(
                detail="Format de fichier incorrect, seuls jpg, pdf, et png sont autorisés",
                code="formulaire_format_incorrect",
            )

        return value

    def validate(self, attrs):
        if attrs["statut"] in [
            RechercheParrainageMaire.Statut.NE_SAIT_PAS,
            RechercheParrainageMaire.Statut.AUTRE_ENGAGEMENT,
        ] and not attrs.get("commentaires"):
            raise serializers.ValidationError(
                detail={"commentaires": "Ce champ est requis avec ce statut."},
                code="commentaires_requis",
            )

        return attrs

    def save(self):
        self.instance.statut = self.validated_data["statut"]
        self.instance.commentaires = self.validated_data.get("commentaires", "")
        self.instance.formulaire = self.validated_data.get("formulaire")
        self.instance.save()
