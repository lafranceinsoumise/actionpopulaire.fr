from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from agir.authentication.tokens import monthly_donation_confirmation_token_generator
from agir.authentication.utils import soft_login
from agir.authentication.view_mixins import VerifyLinkSignatureMixin
from agir.donations import base_views
from agir.ilb.apps import ILBAppConfig
from agir.ilb.forms import PersonalInformationForm, Regularite, date_prelevement
from agir.payments.actions.payments import create_payment, redirect_to_payment
from agir.payments.actions.subscriptions import (
    create_subscription,
    redirect_to_subscribe,
)

from agir.donations.tasks import send_monthly_donation_confirmation_email
from agir.payments.models import display_date_prelevement
from agir.payments.payment_modes import PAYMENT_MODES
from agir.people.models import Person

ILB_DONATION_NAMESPACE = "_ilb_"


class PersonalInformationView(base_views.BasePersonalInformationView):
    payment_type = ILBAppConfig.DONATION_TYPE
    subscription_type = ILBAppConfig.DONATION_TYPE
    session_namespace = ILB_DONATION_NAMESPACE
    first_step_url = settings.ILB_DONS_URL
    template_name = "ilb/dons/personal_information.html"
    form_class = PersonalInformationForm
    persisted_data = ["amount", "regularite"]

    payment_modes = ["system_pay_ilb", "check_ilb"]

    def form_valid(self, form):
        if form.connected:
            person = form.save()
            email = person.email
        else:
            person = None
            email = form.cleaned_data["email"]

        regularite = form.cleaned_data["regularite"]
        # seul le mode de paiement par carte bleue devrait être possible en cas de don régulier
        payment_mode = form.cleaned_data["payment_mode"].id
        amount = form.cleaned_data["amount"]
        meta = self.get_metas(form)

        if regularite == Regularite.PONCTUEL:
            payment = create_payment(
                person=person,
                email=email,
                type=self.payment_type,
                mode=payment_mode,
                price=amount,
                meta=meta,
            )

            return redirect_to_payment(payment)
        elif person is None:
            contact_phone = ""
            if form.cleaned_data.get("contact_phone"):
                contact_phone = form.cleaned_data.pop("contact_phone").as_e164
            send_monthly_donation_confirmation_email.delay(
                data={
                    **form.cleaned_data,
                    "payment_mode": payment_mode,
                    "contact_phone": contact_phone,
                },
                confirmation_view_name="ilb:monthly_donation_confirm",
                email_template="ilb/dons/confirmation_email.html",
            )
            self.clear_session()

            return HttpResponseRedirect(
                reverse("monthly_donation_confirmation_email_sent")
            )

        with transaction.atomic():
            day_of_month = form.cleaned_data.get("day_of_month")
            month_of_year = form.cleaned_data.get("month_of_year")

            subscription = create_subscription(
                person=person,
                type=self.subscription_type,
                mode=payment_mode,
                amount=amount,
                meta=meta,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
            )

        self.clear_session()
        return redirect_to_subscribe(subscription)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["frequence"] = ""
        if self.persistent_data["regularite"] != Regularite.PONCTUEL:
            kwargs["frequence"] = (
                "par an"
                if self.persistent_data["regularite"] == Regularite.ANNUEL
                else "par mois"
            )
            kwargs["date_prelevement"] = display_date_prelevement(
                **date_prelevement(self.persistent_data["regularite"])
            )

        return kwargs


class MonthlyDonationEmailConfirmationView(VerifyLinkSignatureMixin, View):
    session_namespace = ILB_DONATION_NAMESPACE
    payment_mode = PAYMENT_MODES["system_pay_ilb"]
    payment_type = ILBAppConfig.DONATION_TYPE

    def get(self, request, *args, **kwargs):
        params = request.GET.dict()

        token = params.pop("token")
        if not monthly_donation_confirmation_token_generator.check_token(
            token, **params
        ):
            return self.link_error_page()

        try:
            email = params.pop("email")
            amount = int(params.pop("amount"))
            day_of_month = int(params.pop("day_of_month"))
            month_of_year = (
                int(params.pop("month_of_year")) if "month_of_year" in params else None
            )

        except KeyError:
            return self.link_error_page()

        try:
            person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            person = Person.objects.create_insoumise(
                email=email,
                **{
                    f.name: params[f.name]
                    for f in Person._meta.get_fields()
                    if f.name in params
                },
            )

        soft_login(request, person)

        subscription = create_subscription(
            person=person,
            type=self.payment_type,
            mode=self.payment_mode.id,
            amount=amount,
            meta=params,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
        )

        return redirect_to_subscribe(subscription)
