from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.decorators import cache
from django.views.generic import RedirectView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


from agir.donations import base_views
from agir.payments.models import Payment
from .apps import CagnottesConfig
from .forms import PersonalInformationForm
from .models import Cagnotte


class CompteurView(APIView):
    permission_classes = (AllowAny,)

    @method_decorator(cache.cache_page(60))
    @method_decorator(cache.cache_control(public=True))
    def get(self, request, slug):
        from .apps import CagnottesConfig

        cagnotte = get_object_or_404(Cagnotte, public=True, slug=slug)

        return Response(
            Payment.objects.completed()
            .filter(type=CagnottesConfig.PAYMENT_TYPE, meta__cagnotte=cagnotte.id)
            .aggregate(totalAmount=Sum("price"))
        )


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


class RemerciementView(RedirectView):
    url = "https://lafranceinsoumise.fr/caisse-de-greve-insoumise-remerciements"
