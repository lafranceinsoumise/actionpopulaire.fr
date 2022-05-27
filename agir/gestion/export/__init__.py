from agir.gestion.models import Reglement
from agir.gestion.typologies import TypeDocument
from agir.lib.admin.utils import get_admin_link

LIBELLES_MODE = {
    Reglement.Mode.VIREMENT: "VIR",
    Reglement.Mode.PRELEV: "PRLVT",
    Reglement.Mode.CHEQUE: "CHQ",
    Reglement.Mode.CARTE: "CB",
    Reglement.Mode.CASH: "ESP",
}


def lien_document(document):
    if document:
        if fichier := document.fichier:
            return fichier.url

        return get_admin_link(document)
    return "-"


def autres_pieces(reglement):
    documents = reglement.depense.documents.exclude(type__in=[TypeDocument.FACTURE])
    return [lien_document(d) for d in documents]
