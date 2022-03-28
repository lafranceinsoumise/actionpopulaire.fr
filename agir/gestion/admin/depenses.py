from django.utils.safestring import mark_safe

from agir.gestion.models import Compte, Reglement
from agir.lib.display import display_price


class DepenseListMixin:
    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display = tuple(
            v if v != "montant" else self.montant_display(request.user)
            for v in list_display
        )
        return list_display

    def montant_(self, obj):
        if obj:
            return display_price(obj.montant, price_in_cents=False)
        return "-"

    montant_.short_description = "Montant"
    montant_.admin_order_field = "montant"

    def montant_interdit(self, obj):
        return mark_safe("<em>montant masqué</em>")

    montant_interdit.short_description = montant_.short_description

    def montant_display(self, role):
        if role.has_perm("gestion.voir_montant_depense"):
            return self.montant_
        comptes = list(
            Compte.objects.filter(
                autorisation__autorisations__contains=["voir_montant_depense"]
            )
        )

        def montant(obj):
            if obj.finalise and obj.compte not in comptes:
                return self.montant_interdit(obj)
            return self.montant_(obj)

        montant.short_description = self.montant_.short_description

        return montant
