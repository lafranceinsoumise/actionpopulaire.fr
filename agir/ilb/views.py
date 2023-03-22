from agir.donations import base_views
from agir.ilb.apps import ILBAppConfig
from agir.ilb.forms import PersonalInformationForm


class PersonalInformationView(base_views.BasePersonalInformationView):
    payment_type = ILBAppConfig.SINGLE_TIME_DONATION_TYPE
    session_namespace = "_ilb_"
    first_step_url = "https://institutlaboetie.fr/dons/"
    template_name = "ilb/dons/personal_information.html"
    form_class = PersonalInformationForm

    payment_modes = ["system_pay_ilb", "check_ilb"]
