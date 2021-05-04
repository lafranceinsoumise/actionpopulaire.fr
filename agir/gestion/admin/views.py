from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, TemplateView

from agir.gestion.admin.forms import ReglementForm
from agir.gestion.models import Reglement, Depense, Commentaire
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


class CacherCommentaireView(AdminViewMixin, TemplateView):
    template_name = "gestion/cacher_commentaire.html"

    def dispatch(self, request, *args, **kwargs):
        self.commentaire = get_object_or_404(Commentaire, pk=kwargs["pk"])
        self.object = self.model_admin.get_queryset(request).get(
            commentaires__pk=kwargs["pk"]
        )

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.commentaire.cache = True
        self.commentaire.save()

        opts = self.model_admin.model._meta
        return HttpResponseRedirect(
            reverse(
                f"admin:{opts.app_label}_{opts.model_name}_change",
                args=(self.object.pk,),
            )
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            commentaire=self.commentaire, object=self.object, **kwargs,
        )
