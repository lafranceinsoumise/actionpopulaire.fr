import reversion

from agir.gestion.models import Document, Reglement, VersionDocument


def merge_document(d1: Document, d2: Document):
    assert d1.id != d2.id
    with reversion.create_revision():
        reversion.set_comment("Fusion de deux documents")
        # champs du document
        d1.precision = d1.precision or d2.precision
        d1.identifiant = d1.identifiant or d2.identifiant

        d1.numero_piece = d1.numero_piece or d2.numero_piece
        d1.date = d1.date or d2.date

        d1.type = d1.type or d2.type
        d1.source_url = d1.source_url or d2.source_url

        # projets
        d1.projets.add(*d2.projets.values_list("id", flat=True))

        # dépenses
        d1.depenses.add(*d2.depenses.values_list("id", flat=True))

        # règlements comme preuve
        Reglement.objects.filter(preuve=d2).update(preuve=d1)

        # règlements comme facture
        Reglement.objects.filter(facture=d2).update(preuve=d1)

        # On transfère les versions
        VersionDocument.objects.filter(document=d2).update(document=d1)

        d2.delete()
