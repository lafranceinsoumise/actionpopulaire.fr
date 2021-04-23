from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.generic import CreateView

from agir.gestion.admin.forms import ReglementForm
from agir.gestion.models import Reglement, Depense
from agir.lib.admin import AdminViewMixin


class AjouterReglementView(AdminViewMixin, CreateView):
    model = Reglement
    form_class = ReglementForm
    template_name = "gestion/ajouter_reglement.html"

    def dispatch(self, request, *args, **kwargs):
        self.depense = get_object_or_404(Depense, pk=kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "depense": self.depense,
        }

    def get_context_data(self, **kwargs):
        kwargs.setdefault("depense", self.depense)

        kwargs = super().get_context_data(**kwargs)

        champs_fournisseurs = (
            "nom_fournisseur",
            "iban_fournisseur",
            "contact_phone_fournisseur",
            "contact_email_fournisseur",
            "location_address1_fournisseur",
            "location_address2_fournisseur",
            "location_city_fournisseur",
            "location_zip_fournisseur",
            "location_country_fournisseur",
        )

        kwargs.update(
            self.get_admin_helpers(
                form=kwargs["form"],
                fieldsets=[
                    (
                        None,
                        {"fields": ("intitule", "mode", "montant", "date", "preuve")},
                    ),
                    (
                        "Sélectionnez un fournisseur existant",
                        {"fields": ("fournisseur",)},
                    ),
                    (
                        "Ou créez un nouveau fournisseur",
                        {"fields": champs_fournisseurs},
                    ),
                ],
            )
        )
        return kwargs
