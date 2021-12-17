from agir.groups.models import Membership
from agir.lib.display import genrer


def genrer_membership(genre, membership_type):
    """
    Returns membership_type french word from the gender given
    """

    if not membership_type:
        return genrer(genre, "Visiteur", "Visiteuse", "Visiteur⋅se")

    author_status = "Statut inconnu"

    if membership_type == Membership.MEMBERSHIP_TYPE_FOLLOWER:
        author_status = genrer(genre, "Abonné", "Abonnée", "Abonné⋅e")
    elif membership_type == Membership.MEMBERSHIP_TYPE_MEMBER:
        author_status = "Membre"
    elif membership_type == Membership.MEMBERSHIP_TYPE_MANAGER:
        author_status = "Membre gestionnaire"
    elif membership_type == Membership.MEMBERSHIP_TYPE_REFERENT:
        author_status = genrer(genre, "Animateur", "Animatrice", "Animateur·ice")

    return author_status
