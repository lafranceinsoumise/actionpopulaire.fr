from operator import itemgetter

from agir.elus.models import (
    MandatDepute,
    MandatDeputeEuropeen,
    MandatRegional,
    MandatDepartemental,
    MandatMunicipal,
    MandatConsulaire,
)

PRIORITES = [
    (MandatDepute, None),
    (MandatDeputeEuropeen, None),
    (MandatRegional, MandatRegional.MANDAT_PRESIDENT),
    (MandatDepartemental, MandatDepartemental.MANDAT_PRESIDENT),
    (MandatMunicipal, MandatMunicipal.MANDAT_MAIRE),
    (MandatRegional, MandatRegional.MANDAT_VICE_PRESIDENT),
    (MandatDepartemental, MandatDepartemental.MANDAT_VICE_PRESIDENT),
    (MandatMunicipal, MandatMunicipal.MANDAT_MAIRE_DA),
    (MandatRegional, None),
    (MandatMunicipal, MandatMunicipal.MANDAT_MAIRE_ADJOINT),
    (MandatDepartemental, None),
    (MandatConsulaire, None),
    (MandatMunicipal, None),
]

_PRIORITES = {
    (M, type): len(PRIORITES) - i
    for i, (M, potential_type) in enumerate(reversed(PRIORITES))
    for type in (
        [None, *(k for k, _ in M.MANDAT_CHOICES)]
        if not potential_type and hasattr(M, "MANDAT_CHOICES")
        else [potential_type]
    )
}


def mandat_principal(person):
    mandats_types = set(M for M, _ in PRIORITES)
    mandats = [
        (m, _PRIORITES.get((M, getattr(m, "mandat", None))))
        for M in mandats_types
        for m in M.objects.actifs().filter(person=person)
    ]

    if not mandats:
        return None

    return sorted(mandats, key=itemgetter(1))[0][0]
