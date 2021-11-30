from django.db.models import TextChoices


class Etat(TextChoices):
    OK = "OK", "Dossier complet"
    WARNING = "WARN", "Problèmes potentiels"
    UNFINISHED = "ERR", "Éléments manquants"


class TypeDocument(TextChoices):
    DEVIS = "DEV", "Devis"
    CONTRAT = "CON", "Contrat"
    FACTURE = "FAC", "Facture"

    JUSTIFICATIF = "JUS", "Justificatif de dépense"
    JUSTIFICATIF_BILLET = "JUS-BIL", "Billet de train"
    JUSTIFICATIF_TRAIN = "JUS-TRAIN", "Justificatif de train"
    JUSTIFICATIF_CARTE_EMBARQUEMENT = "JUS-CEM", "Carte d'embarquement"

    PAIEMENT = "PAY", "Preuve de paiement"
    PAIEMENT_CHEQUE = "PAY-CHK", "Scan du chèque"
    PAIEMENT_TICKET = "PAY-TKT", "Ticket de caisse"

    EXEMPLAIRE = "EXA", "Exemplaire fourni"
    BAT = "EXA-BAT", "BAT"
    TRACT = "EXA-TRA", "Tract"
    AFFICHE = "EXA-AFF", "Affiche"

    PHOTOGRAPHIE = "PHO", "Photographie de l'objet ou de l'événement"
    AUTRE = "AUT", "Autre (à détailler dans les commentaires)"

    ATTESTATION = "ATT"
    ATTESTATION_GRATUITE = "ATT-GRA", "Attestation de gratuité"
    ATTESTATION_CONCOURS_NATURE = "ATT-CON", "Attestation de concours en nature"
    ATTESTATION_REGLEMENT_CONSOMMATIONS = (
        "ATT-REG",
        "Attestation de réglement des consommations",
    )
    DEMANDE_AUTORISATION_ESPACE_PUBLIC = (
        "ATT-ESP",
        "Demande d'autorisation d'occupation de l'espace public",
    )


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

    REFACTURATION = "REF", "Refacturation"


class TypeProjet(TextChoices):
    CONFERENCE_PRESSE = "CON", "Conférence de presse"

    REUNION_PUBLIQUE = "REU", "Réunion publique et meetings"
    REUNION_PUBLIQUE_LOCALE = "REU-loc", "Réunion publique organisée localement"
    REUNION_PUBLIQUE_ORATEUR = "REU-ora", "Réunion publique avec un orateur national"
    REUNION_PUBLIQUE_CANDIDAT = "REU-can", "Réunion publique avec un candidat"
    REUNION_PUBLIQUE_MEETING = "REU-mee", "Meeting"

    DEBATS = "DEB", "Débats et conférences"
    DEBATS_ASSO = "DEB-aso", "Débat organisé par une association"
    DEBATS_CONF = "DEB-con", "Conférence"
    DEBATS_CAFE = "DEB-caf", "Café-débat"
    DEBATS_PROJECTION = "DEB-pro", "Projection et débat"

    MANIFESTATION = "MAN", "Manifestations et événements publics"
    MANIFESTATION_LOCALE = "MAN-loc", "Manifestation ou marche organisée localement"
    MANIFESTATION_NATIONALE = "MAN-nat", "Manifestation ou marche nationale"
    MANIFESTATION_PIQUE_NIQUE = "MAN-pic", "Pique-nique ou apéro citoyen"
    MANIFESTATION_ECOUTE_COLLECTIVE = "MAN-eco", "Écoute collective"
    MANIFESTATION_FETE = "MAN-fet", "Fête (auberge espagnole)"
    MANIFESTATION_CARAVANE = "MAN-car", "Caravane"

    ACTIONS = "ACT", "Autres actions publiques"

    EVENEMENT = "EVE", "Événements spécifiques"
    EVENEMENT_AMFIS = "EVE-AMF", "AMFiS d'été"
    CONVENTION = "EVE-CON", "Convention"

    DEPENSES_RH = "RH", "Dépenses RH mensuelles"


class NiveauAcces(TextChoices):
    SANS_RESTRICTION = "N", "Sans restriction"
    RESTREINT = "R", "Restreint"
    SECRET = "S", "Secret"
