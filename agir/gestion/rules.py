import rules
from .models import Compte

from agir.gestion.models.common import Autorisation
from ..lib.rules import is_authenticated_person


def permission_sur_compte(perm):
    @rules.predicate
    def pred(role, obj=None):
        return (
            obj is not None
            and Autorisation.objects.filter(
                group__user=role, compte=obj, autorisations__contains=[perm]
            ).exists()
        )

    return pred


for perm, _ in Compte._meta.permissions:
    rules.add_perm(
        f"gestion.{perm}", is_authenticated_person & permission_sur_compte(perm)
    )
