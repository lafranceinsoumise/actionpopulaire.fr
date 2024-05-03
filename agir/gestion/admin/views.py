import logging

import reversion
from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.admin.options import get_content_type_for_model
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django.views import View
from django.views.generic import CreateView, TemplateView, FormView

from agir.lib.admin.panels import AdminViewMixin
from agir.lib.display import display_price
from .forms import ReglementForm, CommentaireForm
from ..models import Depense, Commentaire, Reglement, OrdreVirement


logger = logging.getLogger(__name__)


class AjouterReglementView(AdminViewMixin, CreateView):
    model = Reglement
    form_class = ReglementForm
    template_name = "admin/gestion/ajouter_reglement.html"

    def dispatch(self, request, *args, **kwargs):
        self.depense = get_object_or_404(Depense, pk=kwargs.get("object_id"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with reversion.create_revision():
            montant = display_price(form.cleaned_data["montant"], price_in_cents=False)
            message = f"Ajout d'un règlement d'une valeur de {montant}"
            reversion.set_user(self.request.user)
            reversion.set_comment(message)
            LogEntry.objects.log_action(
                user_id=self.request.user.pk,
                content_type_id=get_content_type_for_model(self.depense).pk,
                object_id=self.depense.pk,
                object_repr=str(self.depense),
                action_flag=CHANGE,
                change_message=message,
            )
            return super().form_valid(form)

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "depense": self.depense,
        }

    def get_context_data(self, **kwargs):
        kwargs.setdefault("depense", self.depense)

        kwargs = super().get_context_data(**kwargs)

        champs_fournisseurs = [
            f"{f}_fournisseur" for f in self.form_class.CHAMPS_FOURNISSEURS
        ]

        kwargs.update(
            self.get_admin_helpers(
                form=kwargs["form"],
                fieldsets=[
                    (
                        None,
                        {
                            "fields": (
                                "intitule",
                                "numero",
                                "choix_mode",
                                "montant",
                                "date",
                                "facture",
                                "preuve",
                            )
                        },
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

    def get_success_url(self):
        return reverse("admin:gestion_depense_change", args=(self.depense.id,))


class CacherCommentaireView(AdminViewMixin, TemplateView):
    template_name = "admin/gestion/cacher_commentaire.html"

    def dispatch(self, request, *args, **kwargs):
        self.commentaire = get_object_or_404(Commentaire, pk=kwargs["pk"])
        self.object = self.model_admin.get_queryset(request).get(
            commentaires__pk=kwargs["pk"]
        )

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        with reversion.create_revision():
            e = "e" if self.commentaire.type == Commentaire.Type.REM else ""
            message = (
                f"{self.commentaire.get_type_display()} indiqué{e} comme traité{e}"
            )

            reversion.set_user(request.user)
            reversion.set_comment(message)
            self.commentaire.cache = True
            self.commentaire.save()
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=str(self.object),
                action_flag=CHANGE,
                change_message=message,
            )

        opts = self.model_admin.model._meta
        return HttpResponseRedirect(
            reverse(
                f"admin:{opts.app_label}_{opts.model_name}_change",
                args=(self.object.pk,),
            )
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            commentaire=self.commentaire,
            object=self.object,
            **kwargs,
        )


class FormHandlerView(View):
    model = None

    def lien_incorrect(self, message=None):
        if message is None:
            message = "Le lien que vous avez suivi était incorrect."

        messages.add_message(
            request=self.request,
            level=messages.WARNING,
            message=message,
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
            with reversion.create_revision():
                type = Commentaire.Type(form.cleaned_data["type"])
                e = "e" if type == Commentaire.Type.REM else ""
                message = f"Ajout d'un{e} {type.label}"
                reversion.set_user(request.user)
                reversion.set_comment(message)
                form.save(self.object)
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=get_content_type_for_model(self.object).pk,
                    object_id=self.object.pk,
                    object_repr=str(self.object),
                    action_flag=CHANGE,
                    change_message=message,
                )
            return super().retour_page_modification()

        return self.lien_incorrect()


class TransitionView(FormHandlerView):
    def post(self, request, *args, **kwargs):
        role = request.user

        try:
            etat_suivant = self.object.Etat(request.POST.get("etat"))
        except ValueError:
            return self.lien_incorrect()

        etat_actuel = self.object.Etat(self.object.etat)

        try:
            transition = next(
                t
                for t in self.model.TRANSITIONS.get(etat_actuel)
                if t.vers == etat_suivant
            )
        except StopIteration:
            return self.lien_incorrect()

        if refus := transition.refus(self.object, role):
            return self.lien_incorrect(message=refus)

        with reversion.create_revision():
            comment = f"{transition.nom} ({etat_actuel.label} => {etat_suivant.label})"
            reversion.set_user(request.user)
            reversion.set_comment(comment)
            transition.appliquer(self.object)
            self.object.save()

            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=get_content_type_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=str(self.object),
                action_flag=CHANGE,
                change_message=comment,
            )

        return self.retour_page_modification()


class ObtenirFichierOrdreVirementView(View):
    def get(self, request, *args, object_id, **kwargs):
        obj = get_object_or_404(OrdreVirement, id=object_id)

        if not obj.fichier:
            try:
                obj.generer_fichier_virement()
            except ValueError as e:
                logger.error(
                    "Erreur lors de la génération d'un fichier de virement",
                    exc_info=True,
                )
                messages.add_message(
                    request,
                    messages.WARNING,
                    format_html(
                        "<p>{}</p><p>{}</p>",
                        "Une erreur a été rencontré lors de la génération du fichier de virement. Merci de consulter les"
                        " logs pour obtenir les détails.",
                        e.args[0],
                    ),
                )

                return HttpResponseRedirect(
                    reverse("admin:gestion_ordrevirement_change", args=(obj.id,))
                )

        with obj.fichier.open("r") as fd:
            res = HttpResponse(
                fd.read(),
                content_type="application/xml",
            )
        res["Content-Disposition"] = (
            f'attachment; filename="ordre_virement_{obj.id}.xml"'
        )
        return res
