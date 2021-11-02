import json

from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, FormView
from functools import partial

from agir.authentication.tokens import monthly_donation_confirmation_token_generator
from agir.authentication.utils import soft_login
from agir.authentication.view_mixins import VerifyLinkSignatureMixin
from agir.donations.allocations import create_monthly_donation
from agir.donations.apps import DonsConfig
from agir.donations.base_views import BaseAskAmountView, BasePersonalInformationView
from agir.donations.forms import AlreadyHasSubscriptionForm
from agir.front.view_mixins import SimpleOpengraphMixin
from agir.groups.models import SupportGroup
from agir.payments import payment_modes
from agir.payments.actions.payments import (
    find_or_create_person_from_payment,
    redirect_to_payment,
    create_payment,
)
from agir.payments.actions.subscriptions import (
    redirect_to_subscribe,
    replace_subscription,
)
from agir.payments.models import Payment, Subscription
from agir.people.models import Person
from agir.donations import forms
from agir.donations.form_fields import (
    serialize_allocations,
    deserialize_allocations,
    sum_allocations,
)
from agir.donations.models import Operation
from agir.donations.tasks import (
    send_donation_email,
    send_monthly_donation_confirmation_email,
)

__all__ = (
    "AskAmountView",
    "DonationPersonalInformationView",
    "MonthlyDonationPersonalInformationView",
    "MonthlyDonationEmailSentView",
    "MonthlyDonationEmailConfirmationView",
    "AlreadyHasSubscriptionView",
    "ReturnView",
    "notification_listener",
    "subscription_notification_listener",
    "DONATION_SESSION_NAMESPACE",
)

DONATION_SESSION_NAMESPACE = "_donation_"


class AskAmountView(SimpleOpengraphMixin, BaseAskAmountView):
    meta_title = "Je donne à la France insoumise"
    meta_description = (
        "Pour financer les dépenses liées à l’organisation d’événements, à l’achat de matériel, au"
        "fonctionnement du site, etc., nous avons besoin du soutien financier de chacun.e d’entre vous !"
    )
    meta_type = "website"

    form_class = forms.AllocationDonationForm
    template_name = "donations/ask_amount.html"
    success_url = reverse_lazy("donation_information")
    session_namespace = DONATION_SESSION_NAMESPACE

    def dispatch(self, request, *args, **kwargs):
        self.group = None
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if "group" in request.GET:
            try:
                self.group = SupportGroup.objects.get(pk=request.GET["group"])
            except SupportGroup.DoesNotExist:
                pass
        return super().get(request, *args, **kwargs)

    def get_meta_title(self):
        if self.group is not None:
            return f"J'aide {self.group.name}"
        return super().get_meta_title()

    def get_meta_description(self):
        if self.group is not None:
            return (
                f"Pour financer les dépenses liées à ses activités, le groupe d'action « {self.group.name} » a"
                f" besoin de votre aide !"
            )
        return super().get_meta_description()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["group_id"] = self.request.GET.get("group")
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        if self.group is not None:
            kwargs["donation_title"] = f"J'aide {self.group.name}"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        if (
            "type" in form.cleaned_data
            and form.cleaned_data["type"] == form.TYPE_MONTHLY
        ):
            self.success_url = reverse("monthly_donation_information")

        return super().form_valid(form)


class AllocationPersonalInformationMixin:
    persisted_data = ["amount", "allocations"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"]["allocations"] = self.persistent_data.get("allocations", {})
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["national"] = context_data["amount"] - sum(
            context_data["allocations"].values()
        )

        return context_data


@method_decorator(never_cache, name="get")
class DonationPersonalInformationView(
    AllocationPersonalInformationMixin, BasePersonalInformationView
):
    form_class = forms.AllocationDonorForm
    template_name = "donations/personal_information.html"
    payment_type = DonsConfig.PAYMENT_TYPE
    session_namespace = DONATION_SESSION_NAMESPACE
    first_step_url = "donation_amount"

    def get_metas(self, form):
        meta = super().get_metas(form)

        allocations = form.cleaned_data["allocations"]

        if allocations:
            meta["allocations"] = json.dumps(
                {str(k.pk): v for k, v in allocations.items()}
            )

        return meta

    def form_valid(self, form):
        if form.connected:
            self.object = form.save()
        amount = form.cleaned_data["amount"]
        payment_metas = self.get_metas(form)

        payment_fields = [f.name for f in Payment._meta.get_fields()]

        kwargs = {f: v for f, v in form.cleaned_data.items() if f in payment_fields}
        if "email" in form.cleaned_data:
            kwargs["email"] = form.cleaned_data["email"]

        kwargs["mode"] = kwargs["mode"].id

        with transaction.atomic():
            payment = create_payment(
                person=self.object,
                type=self.payment_type,
                price=amount,
                meta=payment_metas,
                **kwargs,
            )

        self.clear_session()

        return redirect_to_payment(payment)


class MonthlyDonationPersonalInformationView(
    AllocationPersonalInformationMixin, BasePersonalInformationView
):
    form_class = forms.AllocationMonthlyDonorForm
    template_name = "donations/personal_information.html"
    payment_mode = payment_modes.DEFAULT_MODE
    payment_type = DonsConfig.SUBSCRIPTION_TYPE
    session_namespace = DONATION_SESSION_NAMESPACE
    first_step_url = "view_payments"
    persisted_data = ["amount", "allocations", "previous_subscription"]
    confirmation_view_name = "monthly_donation_confirm"

    def get_context_data(self, **context_data):
        return super().get_context_data(monthly=True, **context_data)

    def get_metas(self, form):
        meta = super().get_metas(form)

        meta["allocations"] = serialize_allocations(form.cleaned_data["allocations"])

        if form.cleaned_data["previous_subscription"]:
            meta["previous_subscription"] = form.cleaned_data[
                "previous_subscription"
            ].pk

        return meta

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        allocations = form.cleaned_data["allocations"]
        previous_subscription = form.cleaned_data["previous_subscription"]

        if form.connected:
            # une personne connectée a rempli le formulaire
            self.object = form.save()

            if (
                Subscription.objects.filter(
                    person=self.object,
                    status=Subscription.STATUS_ACTIVE,
                    mode=self.payment_mode,
                )
                and not previous_subscription
            ):
                # stocker toutes les infos en session
                # attention à ne pas juste modifier le dictionnaire existant,
                # parce que la session ne se "rendrait pas compte" qu'elle a changé
                # et cela ne serait donc pas persisté
                self.request.session[self.session_namespace] = {
                    "new_subscription": {
                        "type": self.payment_type,
                        "mode": self.payment_mode,
                        "subscription_total": amount,
                        "meta": self.get_metas(form),
                    },
                    **self.request.session.get(self.session_namespace, {}),
                }
                return HttpResponseRedirect(reverse("already_has_subscription"))

            with transaction.atomic():
                subscription = create_monthly_donation(
                    person=self.object,
                    mode=self.payment_mode,
                    subscription_total=amount,
                    allocations=allocations,
                    meta=self.get_metas(form),
                    type=self.payment_type,
                )

            self.clear_session()

            if previous_subscription:
                replace_subscription(
                    previous_subscription=previous_subscription,
                    new_subscription=subscription,
                )

                return HttpResponseRedirect(reverse("view_payments"))
            else:
                return redirect_to_subscribe(subscription)
        else:
            send_monthly_donation_confirmation_email.delay(
                confirmation_view_name=self.confirmation_view_name,
                email=form.cleaned_data["email"],
                subscription_total=amount,
                **self.get_metas(form),
            )
            return HttpResponseRedirect(
                reverse("monthly_donation_confirmation_email_sent")
            )


class MonthlyDonationEmailSentView(TemplateView):
    template_name = "donations/monthly_donation_confirmation_email_sent.html"


@method_decorator(never_cache, name="get")
class AlreadyHasSubscriptionView(FormView):
    template_name = "donations/already_has_subscription.html"
    form_class = AlreadyHasSubscriptionForm
    session_namespace = DONATION_SESSION_NAMESPACE
    first_step_url = "view_payments"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # compliqué d'utiliser SoftLoginRequiredMixin parce qu'on doit redéfinir dispatch
            # par ailleurs on veut plutôt rediriger vers le profil que revenir sur cette page
            return redirect(self.first_step_url)

        if (
            self.session_namespace not in request.session
            or "new_subscription" not in request.session[self.session_namespace]
        ):
            return redirect(self.first_step_url)

        self.new_subscription_info = self.request.session[self.session_namespace][
            "new_subscription"
        ]
        self.new_subscription_info["allocations"] = self.new_subscription_info[
            "allocations"
        ] = deserialize_allocations(self.new_subscription_info["meta"]["allocations"])

        self.old_subscription = Subscription.objects.filter(
            person=request.user.person,
            status=Subscription.STATUS_ACTIVE,
            mode=self.new_subscription_info["mode"],
            type=self.new_subscription_info["type"],
        ).first()

        if self.old_subscription is None:
            return redirect(self.first_step_url)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        replace_amount = self.new_subscription_info["subscription_total"]
        replace_allocations = self.new_subscription_info["allocations"]

        add_amount = replace_amount + self.old_subscription.price
        add_allocations = sum_allocations(
            self.new_subscription_info["allocations"],
            {a.group: a.amount for a in self.old_subscription.allocations.all()},
        )

        return super().get_context_data(
            replace_amount=replace_amount,
            replace_national=replace_amount - sum(replace_allocations.values()),
            replace_allocations=[
                (g.name, a)
                for g, a in self.new_subscription_info["allocations"].items()
            ],
            add_amount=add_amount,
            add_national=add_amount - sum(add_allocations.values()),
            add_allocations=[(g.name, a) for g, a in add_allocations.items()],
        )

    def form_valid(self, form):
        choice = form.cleaned_data["choice"]

        if choice == "A":
            self.new_subscription_info[
                "subscription_total"
            ] += self.old_subscription.price
            self.new_subscription_info["allocations"] = sum_allocations(
                self.new_subscription_info["allocations"],
                {a.group: a.amount for a in self.old_subscription.allocations.all()},
            )

        with transaction.atomic():
            new_subscription = create_monthly_donation(
                person=self.request.user.person, **self.new_subscription_info
            )

            replace_subscription(
                previous_subscription=self.old_subscription,
                new_subscription=new_subscription,
            )

        del self.request.session[self.session_namespace]
        return HttpResponseRedirect(reverse("view_payments"))


@method_decorator(never_cache, name="get")
class MonthlyDonationEmailConfirmationView(VerifyLinkSignatureMixin, View):
    session_namespace = DONATION_SESSION_NAMESPACE
    payment_mode = payment_modes.DEFAULT_MODE
    payment_type = DonsConfig.SUBSCRIPTION_TYPE

    def get(self, request, *args, **kwargs):
        params = request.GET.dict()

        if not all(
            param in params
            for param in monthly_donation_confirmation_token_generator.token_params
        ):
            return self.link_error_page()

        token = params.pop("token")
        if not monthly_donation_confirmation_token_generator.check_token(
            token, **params
        ):
            return self.link_error_page()

        try:
            email = params.pop("email")
            subscription_total = int(params.pop("subscription_total"))
            raw_allocations = params.get("allocations")
        except KeyError:
            return self.link_error_page()

        allocations = {}

        if raw_allocations:
            try:
                raw_allocations = json.loads(raw_allocations)
            except ValueError:
                pass
            else:
                for group_pk, allocation_amount in raw_allocations.items():
                    try:
                        allocations[
                            SupportGroup.objects.get(pk=group_pk)
                        ] = allocation_amount
                    except SupportGroup.DoesNotExist:
                        continue

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

        known_previous_subscription = params.get(
            "previous_subscription"
        )  # get et non pas pop, on le garde dans le META
        if known_previous_subscription:
            try:
                known_previous_subscription = Subscription.objects.get(
                    pk=known_previous_subscription
                )
            except Subscription.DoesNotExist:
                known_previous_subscription = None
            else:
                if known_previous_subscription.mode != self.payment_mode:
                    known_previous_subscription = None
                elif known_previous_subscription.person != person:
                    known_previous_subscription = None

        if (
            Subscription.objects.filter(
                person=person, status=Subscription.STATUS_ACTIVE
            ).exists()
            and not known_previous_subscription
        ):
            self.request.session[self.session_namespace] = {
                "new_subscription": {
                    "mode": self.payment_mode,
                    "subscription_total": subscription_total,
                    "meta": params,
                },
                **self.request.session.get(self.session_namespace, {}),
            }
            return redirect("already_has_subscription")

        subscription = create_monthly_donation(
            person=person,
            mode=self.payment_mode,
            subscription_total=subscription_total,
            allocations=allocations,
            meta=params,
            type=self.payment_type,
        )

        if known_previous_subscription:
            replace_subscription(
                previous_subscription=known_previous_subscription,
                new_subscription=subscription,
            )

            return HttpResponseRedirect(reverse("view_payments"))
        else:
            return redirect_to_subscribe(subscription)


class ReturnView(TemplateView):
    template_name = "donations/thanks.html"


def subscription_notification_listener(subscription):
    if subscription.status == Subscription.STATUS_ACTIVE:
        transaction.on_commit(
            partial(
                send_donation_email.delay, subscription.person.pk, subscription.mode
            )
        )


def notification_listener(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        with transaction.atomic():
            find_or_create_person_from_payment(payment)
            if payment.subscription is None:
                transaction.on_commit(
                    partial(send_donation_email.delay, payment.person.pk, payment.type)
                )

                allocations = {}
                if "allocations" in payment.meta:
                    try:
                        allocations = json.loads(payment.meta["allocations"])
                    except ValueError:
                        pass

                for group_id, amount in allocations.items():
                    try:
                        group = SupportGroup.objects.get(pk=group_id)
                    except SupportGroup.DoesNotExist:
                        continue

                    Operation.objects.update_or_create(
                        payment=payment, group=group, defaults={"amount": amount}
                    )
            else:
                for allocation in payment.subscription.allocations.all():
                    Operation.objects.update_or_create(
                        payment=payment,
                        group=allocation.group,
                        defaults={"amount": allocation.amount},
                    )
