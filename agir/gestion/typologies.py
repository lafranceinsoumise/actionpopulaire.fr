from django.db.models import TextChoices


class Etat(TextChoices):
    OK = "OK", "Dossier complet"
    WARNING = "WARN", "Problèmes potentiels"
    UNFINISHED = "ERR", "Éléments manquants"


class NiveauAcces(TextChoices):
    NON_RESTREINT = "N"
    RESTREINT = "R"
    FINANCES_SEULEMENT = "F"


class TypeDocument(TextChoices):
    DEVIS = "DEV", "Devis"
    FACTURE = "FAC", "Facture"
    JUSTIFICATIF = "JUS", "Justificatif de dépense"
    PAIEMENT = "PAY", "Preuve de paiement"
    ATTESTATION_GRATUITE = "GRA", "Attestation de gratuité"
    AUTRE = "AUT", "Autre (à détailler dans les commentaires)"


class TypeDepense(TextChoices):
    FOURNITURE_MARCHANDISES = "AFM", "Achats de fournitures et marchandises"
    FOURNITURE_BUREAU = "AFM-B", "Achats de fourniture de bureau"
    FOURNITURE_GOODIES = "AFM-G", "Achats de goodies"

    FRAIS_BANCAIRES = "FBC", "Frais bancaires"

    FRAIS_DIVERS = "FDV", "Frais divers"

    FRAIS_RECEPTION_HEBERGEMENT = "FRH", "Frais de réception et d'hébergement"
    FRAIS_HEBERGEMENT = "FRH-H", "Frais d'hébergement"
    FRAIS_ALIMENTATION = "FRH-A", "Frais de restauration"

    HONORAIRES_EXPERT_COMPTABLE = "HEC", "Honoraires de l'expert comptable"

    HONORAIRES_CONSEILS_COMMUNICATION = "HCC", "Honoraires et conseils en communication"
    GRAPHISME_MAQUETTAGE = "HCC-G", "Graphisme et maquettage"
    CONSEIL_COMMUNICATION = "HCC-C", "Conseil en communication"

    FRAIS_IMMOBILIERS = "IMM", "Location ou mise à disposition immobilière"
    LOCATION_SALLE_EVENEMENT = "IMM-S", "Mise à disposition d'une salle"
    LOYERS = "IMM-L", "Loyers de location"

    PRODUCTION_AUDIOVISUELLE = "PAU", "Production audiovisuelle"

    PUBLICATION_IMPRESSION = "PIM", "Publication et impression (hors R39)"

    REUNIONS_PUBLIQUES = "REU", "Frais divers liées aux réunions publiques"

    TRANSPORTS = "TRA", "Transports et déplacement"
    TRAIN = (
        "TRA-T",
        "Billets de train",
    )
    AVION = "TRA-A", "Billets d'avion"
    LOCATION_VEHICULE = "TRA-L", "Location d'un véhicule"
    FRAIS_KILOMETRIQUES = "TRA-K", "Frais kilométriques"

    @classmethod
    def hierarchical_choices(cls):
        return [
            (value, f"- {label}" if len(value) > 3 else label)
            for value, label in cls.choices
        ]


class TypeProjet(TextChoices):
    CONFERENCE_PRESSE = "CON", "Conférence de presse"
    REUNION_PUBLIQUE = "REU", "Réunion publique"
    REUNION_PUBLIQUE_LOCALE = "REU-loc", "Réunion publique organisée localement"
    REUNION_PUBLIQUE_ORATEUR = "REU-ora", "Réunion publique avec un orateur national"
    REUNION_PUBLIQUE_CANDIDAT = "REU-can", "Réunion publique avec un candidat"

    DEBATS = "DEB", "Débats et conférences"
    DEBATS_ASSO = "DEB-aso", "Débat organisé par une association"
    DEBATS_CONF = "DEB-con", "Conférence"
    DEBATS_CAFE = "DEB-caf", "Café-débat"

    MANIFESTATION = "MAN", "Manifestation publique"
    MANIFESTATION_LOCALE = "MAN-loc", "Manifestation ou marche organisée localement"
    MANIFESTATION_NATIONALE = "MAN-nat", "Manifestation ou marche nationale"

    ACTIONS = "ACT", "Actions"

    DEPENSES_RH = "RH", "Dépenses RH mensuelles"
