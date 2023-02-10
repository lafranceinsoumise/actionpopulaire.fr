from functools import partial

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators import cache
from django.views.generic import RedirectView
from django.views.generic.detail import BaseDetailView
from rest_framework.generics import get_object_or_404 as rf_get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from agir.donations import base_views
from agir.payments.actions.payments import find_or_create_person_from_payment
from agir.payments.models import Payment
from .actions import montant_cagnotte
from .apps import CagnottesConfig
from .forms import PersonalInformationForm
from .models import Cagnotte
from .tasks import envoyer_email_remerciement
from ..front.view_mixins import ReactBaseView
from ..lib.utils import front_url


class CompteurView(APIView):
    permission_classes = (AllowAny,)

    @method_decorator(cache.cache_page(60))
    @method_decorator(cache.cache_control(public=True))
    def get(self, request, slug):
        cagnotte = rf_get_object_or_404(Cagnotte, public=True, slug=slug)

        return Response({"totalAmount": montant_cagnotte(cagnotte)})


class PersonalInformationView(base_views.BasePersonalInformationView):
    payment_type = CagnottesConfig.PAYMENT_TYPE
    payment_modes = ["system_pay", "check_donations"]
    session_namespace = "_cagnotte_"
    first_step_url = "https://caissedegreveinsoumise.fr"
    template_name = "cagnottes/personal_information.html"
    form_class = PersonalInformationForm

    # noinspection PyMethodOverriding
    def dispatch(self, request, *args, slug, **kwargs):
        self.cagnotte = get_object_or_404(Cagnotte, slug=slug, public=True)
        return super().dispatch(request, *args, **kwargs)

    def get_metas(self, form):
        return {**super().get_metas(form), "cagnotte": self.cagnotte.id}

    def get_context_data(self, **kwargs):
        if "cagnotte" not in kwargs:
            kwargs["cagnotte"] = self.cagnotte
        return super().get_context_data(**kwargs)


class RemerciementView(RedirectView):
    def get_redirect_url(self, *args, payment=None, **kwargs):
        if "cagnotte" in payment.meta:
            try:
                return Cagnotte.objects.get(
                    id=payment.meta["cagnotte"]
                ).url_remerciement
            except (Cagnotte.DoesNotExist, ValueError):
                pass
        return "/"


def notification_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        with transaction.atomic():
            # Dans le cas où il s'agissait d'un paiement réalisé sans session ouverte, l'utilisateur devait saisir son
            # adresse email. On récupère la personne associée à cette adresse email, ou on la crée, et on l'associe à
            # ce paiement.
            find_or_create_person_from_payment(payment)

            transaction.on_commit(
                partial(
                    envoyer_email_remerciement.delay,
                    payment.pk,
                )
            )


class ProgressView(BaseDetailView, ReactBaseView):
    queryset = Cagnotte.objects.all()
    app_mount_id = "cagnottes_app"
    bundle_name = "cagnottes/progress"
    template_name = "cagnottes/progress.html"

    def get_api_preloads(self):
        return [
            reverse_lazy("cagnottes:compteur", kwargs=self.kwargs),
        ]

    def get_context_data(self, **kwargs):
        export_data = {
            "slug": self.kwargs.get("slug"),
            "amountAPI": front_url("cagnottes:compteur", kwargs=self.kwargs),
        }
        if self.object and "progress" in self.object.meta:
            export_data.update({**self.object.meta.get("progress", {})})
        kwargs.update(
            {
                "export_data": export_data,
                "data_script_id": "cagnottes_data",
            }
        )
        return super().get_context_data(**kwargs)
