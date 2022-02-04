from django.db.models import TextChoices


class Etat(TextChoices):
    OK = "OK", "Dossier complet"
    WARNING = "WARN", "Problèmes potentiels"
    UNFINISHED = "ERR", "Éléments manquants"


class TypeDocument(TextChoices):
    DEVIS = "DEV", "Devis"
    CONTRAT = "CON", "Contrat"

    FACTURE = "FAC", "Facture"
    FACTURE_AVOIR = "FAC-AVO", "Facture d'avoir"

    BDL = "BDL", "Bon de livraison"

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
    CAPTURE = "EXA-CAP", "Capture d'écran"

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
    def __new__(cls, value, compte=None):
        """Stocke le numéro de compte à utiliser pour la comptabilité pour chaque catégorie"""
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.compte = compte
        return obj

    REUNIONS_PUBLIQUES = "REU", "613", "Frais divers liées aux réunions publiques"
    IMPRESSION_REUNIONS = (
        "REU-IMP",
        "6131",
        "Impression et envoi de cartons d'invitation pour une réunion publique",
    )
    UTILISATION_LOCAL_REUNIONS = (
        "REU-LOC",
        "6132",
        "Utilisation d'un local pour les besoins d'une réunion publique",
    )
    AMENAGEMENT_LOCAL_REUNIONS = "REU-AME", "6133", "Aménagements apportés au local "
    ECLAIRAGE_SONORISATION_REUNIONS = "REU-EC", "6134", "Éclairage et sonorisation"
    SERVICE_ORDRE_REUNIONS = "REU-ORD", "6135", "Éclairage et sonorisation"
    AUTRES_FRAIS_REUNIONS = (
        "REU-AUT",
        "6136",
        "Autres frais liés à une réunion publique",
    )

    PUBLICATION_IMPRESSION = "PIM", "614", "Publication et impression (hors R39)"
    CONCEPTION_IMPRESSION = "PIM-CON", "6141", "Frais de conception et d'impression"
    FRAIS_POSTAUX = "PIM-POS", "6142", "Frais de distribution et postaux"
    FRAIS_PROMOTION = "PIM-PRO", "6143", "Frais de promotion"
    AUTRE_FRAIS_IMPRESSION = (
        "PIM-AUT",
        "6144",
        "Autres frais d'impression et de publication",
    )

    FOURNITURE_MARCHANDISES = "AFM", None, "Achats de fournitures et marchandises"
    FOURNITURE_BUREAU = "AFM-B", "635", "Achats de fourniture de bureau"
    FOURNITURE_GOODIES = "AFM-G", "621", "Achats de goodies"
    FOURNITURE_MATERIEL = "AFM-M", "634", "Dépenses de matériel"

    FRAIS_BANCAIRES = "FBC", "636", "Frais bancaires"

    FRAIS_DIVERS = "FDV", "637", "Frais divers"

    FRAIS_RECEPTION_HEBERGEMENT = "FRH", "630", "Frais de réception et d'hébergement"
    FRAIS_HEBERGEMENT = "FRH-H", "630", "Frais d'hébergement"
    FRAIS_ALIMENTATION = "FRH-A", "630", "Frais de restauration"

    HONORAIRES_EXPERT_COMPTABLE = "HEC", "633", "Honoraires de l'expert comptable"

    HONORAIRES_CONSEILS_COMMUNICATION = (
        "HCC",
        "623",
        "Honoraires et conseils en communication",
    )

    FRAIS_IMMOBILIERS = "IMM", None, "Location ou mise à disposition immobilière"
    LOYERS_LOCAL = "IMM-L", "6281", "Loyers de location"
    TRAVAUX_LOCAL = "IMM-T", "6282", "Travaux au local"
    AUTRES_FRAIS_IMMOBILIERS = "IMM-AUT", "6283", "Autres frais immobiliers"

    PROPAGANDE_AUDIOVISUELLE = "PAU", None, "Propagande audiovisuelle"
    CONCEPTION_AUDIOVISUELLE = (
        "PAU-CON",
        "6171",
        "Frais de conception et de réalisation audiovisuelle",
    )
    DIFFUSION_AUDIOVISUELLE = (
        "PAU-DIS",
        "6172",
        "Frais de reproduction, diffusion et de distribution audiovisuelle",
    )
    PROMOTION_AUDIOVISUELLE = "PAU-PRO", "6173", "Frais de promotion audiovisuelle"
    AUTRES_AUDIOVISUELLE = "PAU-AUT", "6174", "Autres frais audiovisuels"

    TRANSPORTS = "TRA", "629", "Transports et déplacement"
    TRAIN = "TRA-T", "629", "Billets de train"
    AVION = "TRA-A", "629", "Billets d'avion"
    LOCATION_VEHICULE = "TRA-L", "629", "Location d'un véhicule"
    FRAIS_KILOMETRIQUES = "TRA-K", "629", "Frais kilométriques"

    SALAIRES = "SAL", "624", "Salaires"

    REFACTURATION = "REF", None, "Refacturation"

    # OBSOLÈTE
    GRAPHISME_MAQUETTAGE = "HCC-G", "Graphisme et maquettage", "6141"
    CONSEIL_COMMUNICATION = "HCC-C", "Conseil en communication", "623"
    LOCATION_SALLE_EVENEMENT = "IMM-S", "Mise à disposition d'une salle", "6132"


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


NATURE = (
    "Tracts",
    "Affiches",
    "Flyers",
    "Billets de train",
    "Billets d'avion",
)
