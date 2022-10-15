from django.db.models import Sum
from django.views.decorators import cache
from django.views.generic import RedirectView
from rest_framework.views import APIView

from agir.donations import base_views
from agir.payments.models import Payment
from .apps import CagnottesConfig
from .forms import PersonalInformationForm


class CompteurView(APIView):
    @cache.cache_page(60)
    @cache.cache_control(public=True)
    def get(req):
        from .apps import CagnottesConfig

        return (
            Payment.objects.completed()
            .filter(type=CagnottesConfig.PAYMENT_TYPE)
            .aggregate(totalAmount=Sum("price"))
        )


class PersonalInformationView(base_views.BasePersonalInformationView):
    payment_type = CagnottesConfig.PAYMENT_TYPE
    payment_modes = ["system_pay", "check_donations"]
    session_namespace = "_cagnotte_"
    first_step_url = "https://caissedegreveinsoumise.fr"
    template_name = "cagnottes/personal_information.html"
    form_class = PersonalInformationForm


class RemerciementView(RedirectView):
    url = "https://lafranceinsoumise.fr/caisse-de-greve-insoumise-remerciements"
