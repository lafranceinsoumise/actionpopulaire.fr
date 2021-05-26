from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, FormView

from agir.gestion.admin.forms import ReglementForm, CommentaireForm
from agir.gestion.models import Depense, Commentaire, Reglement
from agir.lib.admin import AdminViewMixin


class AjouterReglementView(AdminViewMixin, CreateView):
    model = Reglement
    form_class = ReglementForm
    template_name = "gestion/ajouter_reglement.html"

    def dispatch(self, request, *args, **kwargs):
        self.depense = get_object_or_404(Depense, pk=kwargs.get("object_id"))
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


class FormHandlerView(View):
    model = None

    def lien_incorrect(self, message=None):
        if message is None:
            message = "Le lien que vous avez suivi était incorrect."

        messages.add_message(
            request=self.request, level=messages.WARNING, message=message,
        )

        return self.retour_page_modification()

    def retour_page_modification(self):
        opts = self.model._meta
        next_url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_change", args=(self.object_id,)
        )
        return HttpResponseRedirect(next_url)

    def dispatch(self, request, *args, **kwargs):
        self.object_id = kwargs["object_id"]
        self.object = get_object_or_404(self.model, pk=self.object_id)

        return super().dispatch(request, *args, **kwargs)


class AjouterCommentaireView(FormView, FormHandlerView):
    model = None

    def post(self, request, *args, **kwargs):
        form = CommentaireForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save(self.object)
            return super().retour_page_modification()

        return self.lien_incorrect()


class TransitionView(FormHandlerView):
    def post(self, request, *args, **kwargs):
        role = request.user

        etat_suivant = request.POST.get("etat")

        if not etat_suivant:
            return self.lien_incorrect()

        try:
            transition = next(
                t
                for t in self.model.TRANSITIONS.get(self.object.etat)
                if t.vers == etat_suivant
            )
        except StopIteration:
            return self.lien_incorrect()

        if refus := transition.refus(self.object, role):
            return self.lien_incorrect(message=refus)

        self.object.etat = transition.vers
        self.object.save(update_fields=["etat"])
        return self.retour_page_modification()
