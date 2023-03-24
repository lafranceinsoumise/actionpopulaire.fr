from urllib.parse import urlencode
from uuid import UUID

from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView, TemplateView, FormView, RedirectView
from django.views.generic.edit import DeleteView

from agir.authentication.tokens import merge_account_token_generator
from agir.authentication.utils import hard_login, is_hard_logged
from agir.authentication.view_mixins import (
    SoftLoginRequiredMixin,
    HardLoginRequiredMixin,
)
from agir.donations.actions import can_make_contribution
from agir.donations.allocations import get_allocation_list
from agir.donations.forms import AllocationSubscriptionForm
from agir.donations.views import DONATION_SESSION_NAMESPACE, AskAmountView
from agir.payments.models import Subscription
from agir.people.actions.management import merge_persons
from agir.people.admin.actions import unsubscribe_from_all_newsletters
from agir.people.forms import (
    Person,
    AddEmailMergeAccountForm,
    VolunteerForm,
    InformationConfidentialityForm,
)
from agir.people.forms.profile import (
    PersonalInformationsForm,
    ContactForm,
    ActivityAndSkillsForm,
)
from agir.people.models import PersonEmail


class ProfileViewMixin(SoftLoginRequiredMixin):
    tab_code = None

    def get_context_data(self, **kwargs):
        kwargs.setdefault("person", self.request.user.person)
        return super().get_context_data(tab_code=self.tab_code, **kwargs)


@method_decorator(never_cache, name="get")
class DeleteAccountView(HardLoginRequiredMixin, DeleteView):
    template_name = "people/profile/delete_account.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse("delete_account_success")

    def get_object(self, queryset=None):
        return self.request.user.person

    def delete(self, request, *args, **kwargs):
        messages.add_message(
            self.request, messages.SUCCESS, "Votre compte a bien été supprimé !"
        )
        response = super().delete(request, *args, **kwargs)
        logout(self.request)

        return response


@method_decorator(never_cache, name="get")
class PersonalInformationsView(ProfileViewMixin, UpdateView):
    template_name = "people/profile/profile_default.html"
    form_class = PersonalInformationsForm
    success_url = reverse_lazy("personal_information")
    tab_code = "IDENTITY"

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


@method_decorator(never_cache, name="get")
class ContactView(SoftLoginRequiredMixin, UpdateView):
    template_name = "people/profile/information_contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def get_context_data(self, **kwargs):
        emails = self.object.emails.all()

        return super().get_context_data(
            person=self.object,
            emails=emails,
            can_delete=self.object.emails.filter(_bounced=False).count() > 1,
            **kwargs,
        )

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person

    def form_valid(self, form):
        res = super().form_valid(form)

        if getattr(form, "no_mail", False):
            unsubscribe_from_all_newsletters(self.request.user.person)
            messages.add_message(
                self.request,
                messages.INFO,
                "Vous êtes maintenant désinscrit⋅e de tous les envois de lettres d'information, SMS et notifications.",
            )

        return res


@method_decorator(never_cache, name="get")
class AddEmailMergeAccountView(SoftLoginRequiredMixin, FormView):
    template_name = "people/profile/account_management.html"
    form_class = AddEmailMergeAccountForm
    success_url = reverse_lazy("confirm_merge_account_sent")

    def get_context_data(self, **kwargs):
        return super().get_context_data(person=self.request.user.person, **kwargs)

    def get_form(self, **kwargs):
        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})

        return AddEmailMergeAccountForm(user_pk=self.request.user.person.pk, **kwargs)

    def form_valid(self, form):
        (email, is_merging) = form.send_confirmation()
        if not email:
            return self.form_invalid(form)
        self.success_url += "?" + urlencode({"email": email, "is_merging": is_merging})
        return super().form_valid(form)


class ConfirmMergeAccountView(View):
    """
    Fusionne 2 compte.

    Cette vue peut être atteinte depuis n'importe quel navigateur donc pas besoin d'être connecté.
    Elle vérifie l'integriter du pk_merge + pk_requester + token
    Elle redirige vers la vue `dashboard` en cas de succès
    En cas de problème vérification du token une page est affiché explicant le problème: `invalid`, `expiration`
    """

    success_url = reverse_lazy("dashboard")
    error_template = "people/confirmation_mail_change_error.html"
    error_messages = {
        "invalid": "Quelque chose d'étrange c'est produit",
        "expired": "Il semble que le lien soit expiré.",
        "same_person": "Il semble que l'opération de fusion à déjà été effectué.",
    }

    def error_page(self, key_error):
        return TemplateResponse(
            self.request,
            [self.error_template],
            context={"message": self.error_messages[key_error]},
        )

    @never_cache
    def get(self, request, **kwargs):
        pk_requester = request.GET.get("pk_requester")
        pk_merge = request.GET.get("pk_merge")
        token = request.GET.get("token")

        # Check part
        if not pk_requester or not pk_merge or not token:
            return self.error_page(key_error="invalid")

        try:
            pk_requester = UUID(pk_requester)
            pk_merge = UUID(pk_merge)
        except ValueError:
            return self.error_page(key_error="invalid")

        try:
            person_requester = Person.objects.get(pk=pk_requester)
            person_merge = Person.objects.get(pk=pk_merge)
        except Person.DoesNotExist:
            return self.error_page(key_error="invalid")

        if merge_account_token_generator.is_expired(token):
            return self.error_page(key_error="expired")

        params = {"pk_requester": str(pk_requester), "pk_merge": str(pk_merge)}
        if not merge_account_token_generator.check_token(token, **params):
            return self.error_page(key_error="invalid")

        try:
            merge_persons(person_requester, person_merge)
        except ValueError:
            return self.error_page(key_error="same_person")

        # success part
        hard_login(request, person_requester)
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Votre fusion de compte à été effectué avec succès",
        )

        return HttpResponseRedirect(self.success_url)


class SendConfirmationMergeAccountView(HardLoginRequiredMixin, TemplateView):
    template_merge = "people/confirmation_change_mail_merge_account_sent.html"
    template_name = "people/profile/confirmation_change_mail_merge_account_sent.html"

    @never_cache
    def get(self, request, *args, **kwargs):
        self.email = request.GET.get("email")
        self.is_merging = True if request.GET.get("is_merging") == "True" else False
        return super().get(request)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            email_to=self.email,
            email_from=self.request.user.person.email,
            is_merging=self.is_merging,
            **kwargs,
        )


class ChangePrimaryEmailView(SoftLoginRequiredMixin, RedirectView):
    url = reverse_lazy("contact")

    @never_cache
    def get(self, request, *args, **kwargs):
        self.person = request.user.person
        email = PersonEmail.objects.get(pk=self.kwargs["pk"])
        email.bounced = False
        email.save()
        self.person.set_primary_email(email)

        return super().get(request, *args, **kwargs)


@method_decorator(never_cache, name="get")
class SkillsView(ProfileViewMixin, UpdateView):
    template_name = "people/profile/profile_default.html"
    form_class = ActivityAndSkillsForm
    success_url = reverse_lazy("skills")
    tab_code = "SKILLS"

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


@method_decorator(never_cache, name="get")
class PersonalDataView(ProfileViewMixin, FormView):
    template_name = "people/profile/profile_default.html"
    form_class = InformationConfidentialityForm
    success_url = reverse_lazy("personal_data")
    tab_code = "PERSONAL_DATA"

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person

    def form_valid(self, form):
        # désabonnement
        person = self.get_object()
        person.newsletters = []
        person.save(update_fields=["newsletters"])
        messages.add_message(
            self.request,
            messages.INFO,
            "Vous êtes maintenant désinscrit·e de toutes les lettres d'information.",
        )
        return self.render_to_response(self.get_context_data())


@method_decorator(never_cache, name="get")
class VolunteerView(ProfileViewMixin, UpdateView):
    template_name = "people/profile/volunteer.html"
    form_class = VolunteerForm
    success_url = reverse_lazy("volunteer")
    tab_code = "ACT"

    def get_object(self, queryset=None):
        """Get the current user as the view object"""
        return self.request.user.person


class PaymentsView(AskAmountView, ProfileViewMixin, TemplateView):
    template_name = "people/profile/payments.html"
    tab_code = "PAYMENTS"
    form_class = AllocationSubscriptionForm
    session_namespace = DONATION_SESSION_NAMESPACE
    success_url = reverse_lazy("donation_information_modal")

    @never_cache
    def get(self, request, *args, **kwargs):
        self.subscriptions = self.get_subscriptions()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.subscriptions = self.get_subscriptions()
        return super().post(request, *args, **kwargs)

    def get_subscriptions(self):
        return self.request.user.person.subscriptions.filter(
            status=Subscription.STATUS_ACTIVE
        )

    def get_initial_for_subscription(self, subscription):
        allocations = get_allocation_list(subscription.allocations)
        initial = {
            "amount": subscription.price,
            "previous_subscription": subscription.pk,
            "allocations": allocations,
        }

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        for subscription in self.subscriptions:
            subscription.modify_form = self.form_class(
                user=self.request.user,
                initial=self.get_initial_for_subscription(subscription),
            )
        kwargs["can_make_contribution"] = can_make_contribution(
            person=self.request.user.person
        )

        return super().get_context_data(
            is_hard_logged=is_hard_logged(self.request),
            pending_payments=self.request.user.person.payments.awaiting().checks(),
            payments=self.request.user.person.payments.completed(),
            subscriptions=self.subscriptions,
            **kwargs,
        )
