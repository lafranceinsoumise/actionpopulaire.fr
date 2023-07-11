from django.db.models import Q


def drawing_eligibility_conditions(reference_date, is_political_support=True):
    cond = Q(
        draw_participation=True,  # les personnes doivent être inscrits explicitement
        role__created__lt=reference_date,  # le compte devait exister avant la date de référence
        role__is_active=True,  # il doit s'agir d'un compte actif,
    )

    if is_political_support:
        cond &= Q(is_political_support=True)

    return cond
