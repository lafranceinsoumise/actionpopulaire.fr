from uuid import UUID

import logging
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views import View
from django.views.generic import DetailView, TemplateView, UpdateView, FormView
from django.views.generic.edit import FormMixin, ProcessFormView

from agir.authentication.tokens import (
    invitation_confirmation_token_generator,
    subscription_confirmation_token_generator,
    abusive_invitation_report_token_generator,
)
from agir.authentication.utils import hard_login
from agir.authentication.view_mixins import (
    HardLoginRequiredMixin,
    PermissionsRequiredMixin,
    VerifyLinkSignatureMixin,
)
from agir.donations.allocations import get_balance
from agir.donations.models import SpendingRequest
from agir.front.view_mixins import ChangeLocationBaseView
from agir.groups.actions import get_next_promo_code
from agir.groups.actions.pressero import is_pressero_enabled, redirect_to_pressero
from agir.groups.actions.promo_codes import is_promo_code_delayed, next_promo_code_date
from agir.groups.forms import (
    AddReferentForm,
    AddManagerForm,
    InvitationForm,
    SupportGroupForm,
    GroupGeocodingForm,
    InvitationWithSubscriptionConfirmationForm,
)
from agir.groups.models import SupportGroup, Membership
from agir.groups.tasks import send_abuse_report_message
from agir.lib.http import add_query_params_to_url
from agir.people.models import Person


__all__ = [
    "SupportGroupManagementView",
    "CreateSupportGroupView",
    "PerformCreateSupportGroupView",
    "ModifySupportGroupView",
    "RemoveManagerView",
    "ChangeGroupLocationView",
    "RedirectToPresseroView",
    "InvitationConfirmationView",
    "InvitationWithSubscriptionView",
    "InvitationAbuseReportingView",
]


logger = logging.getLogger(__name__)


class CheckMembershipMixin:
    def user_is_referent(self):
        return self.user_membership is not None and self.user_membership.is_referent

    def user_is_manager(self):
        return self.user_membership is not None and (
            self.user_membership.is_referent or self.user_membership.is_manager
        )

    @property
    def user_membership(self):
        if not hasattr(self, "_user_membership"):
            if isinstance(self.object, SupportGroup):
                group = self.object
            else:
                group = self.object.supportgroup

            try:
                self._user_membership = group.memberships.get(
                    person=self.request.user.person
                )
            except Membership.DoesNotExist:
                self._user_membership = None

        return self._user_membership


class SupportGroupManagementView(
    HardLoginRequiredMixin, CheckMembershipMixin, DetailView
):
    template_name = "groups/manage.html"
    queryset = SupportGroup.objects.active().all().prefetch_related("memberships")
    messages = {
        "add_referent_form": ugettext_lazy(
            "{email} est maintenant correctement signalé comme second·e animateur·rice."
        ),
        "add_manager_form": ugettext_lazy(
            "{email} a bien été ajouté·e comme gestionnaire pour ce groupe."
        ),
        "invitation_form": ugettext_lazy(
            "{email} a bien été invité à rejoindre votre groupe."
        ),
    }
    need_referent_status = {"add_referent_form", "add_manager_form"}
    active_panel = {
        "add_referent_form": "animation",
        "add_manager_form": "animation",
        "invitation_form": "invitation",
    }

    def get_forms(self):
        kwargs = {}

        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST})

        return {
            "add_referent_form": AddReferentForm(self.object, **kwargs),
            "add_manager_form": AddManagerForm(self.object, **kwargs),
            "invitation_form": InvitationForm(
                group=self.object, inviter=self.request.user.person, **kwargs
            ),
        }

    def get_context_data(self, **kwargs):
        kwargs["referents"] = self.object.memberships.filter(is_referent=True).order_by(
            "created"
        )
        kwargs["managers"] = self.object.memberships.filter(
            is_manager=True, is_referent=False
        ).order_by("created")
        kwargs["members"] = self.object.memberships.all().order_by("created")
        kwargs["has_promo_code"] = self.object.tags.filter(
            label=settings.PROMO_CODE_TAG
        ).exists()
        if kwargs["has_promo_code"]:
            kwargs["group_promo_code"] = get_next_promo_code(self.object)

        if is_promo_code_delayed():
            kwargs["promo_code_delay"] = next_promo_code_date()

        kwargs["certifiable"] = (
            self.object.type in settings.CERTIFIABLE_GROUP_TYPES
            or self.object.subtypes.filter(
                label__in=settings.CERTIFIABLE_GROUP_SUBTYPES
            ).exists()
        )
        kwargs["satisfy_requirements"] = len(kwargs["referents"]) > 1
        kwargs["allocation_balance"] = get_balance(self.object)
        kwargs["spending_requests"] = SpendingRequest.objects.filter(
            group=self.object
        ).exclude(status=SpendingRequest.STATUS_PAID)
        kwargs["is_pressero_enabled"] = is_pressero_enabled()

        kwargs["active"] = self.active_panel.get(self.request.POST.get("form"))

        forms = self.get_forms()
        for form_name, form in forms.items():
            kwargs.setdefault(form_name, form)

        return super().get_context_data(
            is_referent=self.user_membership is not None
            and self.user_membership.is_referent,
            is_manager=self.user_membership is not None
            and (self.user_membership.is_referent or self.user_membership.is_manager),
            **kwargs,
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # only managers can access the page
        if not self.user_is_manager():
            raise PermissionDenied("Vous n'etes pas gestionnaire de ce groupe.")

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_name = request.POST.get("form")

        # only referents can add referents and managers
        if not self.user_is_referent() and form_name in self.need_referent_status:
            raise PermissionDenied(
                "Vous n'êtes pas animateur de ce groupe et ne pouvez donc pas modifier les "
                "animateurs et gestionnaires."
            )

        forms = self.get_forms()
        if form_name in forms:
            form = forms[form_name]
            if form.is_valid():
                params = form.perform()

                messages.add_message(
                    request, messages.SUCCESS, self.messages[form_name].format(**params)
                )
            else:
                return self.render_to_response(
                    self.get_context_data(**{form_name: form})
                )

        return HttpResponseRedirect(
            reverse("manage_group", kwargs={"pk": self.object.pk})
        )


class CreateSupportGroupView(HardLoginRequiredMixin, TemplateView):
    template_name = "groups/create.html"

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        initial = {}

        if person.contact_phone:
            initial["phone"] = person.contact_phone.as_e164

        if person.first_name and person.last_name:
            initial["name"] = "{} {}".format(person.first_name, person.last_name)

        return super().get_context_data(props={"initial": initial}, **kwargs)


class PerformCreateSupportGroupView(HardLoginRequiredMixin, FormMixin, ProcessFormView):
    model = SupportGroup
    form_class = SupportGroupForm

    def get_form_kwargs(self):
        """Add user person profile to the form kwargs"""

        kwargs = super().get_form_kwargs()

        person = self.request.user.person
        kwargs["person"] = person
        return kwargs

    def form_invalid(self, form):
        return JsonResponse({"errors": form.errors}, status=400)

    def form_valid(self, form):
        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre groupe a été correctement créé.",
        )

        form.save()

        return JsonResponse(
            {
                "status": "OK",
                "id": form.instance.id,
                "url": reverse("view_group", args=[form.instance.id]),
            }
        )


class ModifySupportGroupView(
    HardLoginRequiredMixin, PermissionsRequiredMixin, UpdateView
):
    permissions_required = ("groups.change_supportgroup",)
    template_name = "groups/modify.html"
    queryset = SupportGroup.objects.active().all()
    form_class = SupportGroupForm

    def get_form_kwargs(self):
        """Add user person profile to the form kwargs"""
        return {**super().get_form_kwargs(), "person": self.request.user.person}

    def get_success_url(self):
        return reverse("manage_group", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message=format_html(
                _("Les modifications du groupe <em>{}</em> ont été enregistrées."),
                self.object.name,
            ),
        )

        return res


class RemoveManagerView(HardLoginRequiredMixin, CheckMembershipMixin, DetailView):
    template_name = "front/confirm.html"
    queryset = (
        Membership.objects.active()
        .all()
        .select_related("supportgroup")
        .select_related("person")
    )

    def get_context_data(self, **kwargs):
        person = self.object.person

        if person.first_name and person.last_name:
            name = "{} {} <{}>".format(
                person.first_name, person.last_name, person.email
            )
        else:
            name = person.email

        return super().get_context_data(
            title=_("Confirmer le retrait du gestionnaire ?"),
            message=_(
                f"""
            Voulez-vous vraiment retirer {name} de la liste des gestionnaires de ce groupe ?
            """
            ),
            button_text="Confirmer le retrait",
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.user_is_referent():
            raise PermissionDenied(
                "Vous n'êtes pas animateur de cet événement et ne pouvez donc pas modifier les "
                "animateurs et gestionnaires."
            )

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # user has to be referent, and target user cannot be a referent
        if not self.user_is_referent() or self.object.is_referent:
            raise PermissionDenied(
                "Vous n'êtes pas animateur de cet événement et ne pouvez donc pas modifier les "
                "animateurs et gestionnaires."
            )

        self.object.is_manager = False
        self.object.save()

        messages.add_message(
            request,
            messages.SUCCESS,
            _("{} n'est plus un gestionnaire du groupe.").format(
                self.object.person.email
            ),
        )

        return HttpResponseRedirect(
            reverse_lazy("manage_group", kwargs={"pk": self.object.supportgroup_id})
        )


class ChangeGroupLocationView(ChangeLocationBaseView):
    template_name = "groups/change_location.html"
    form_class = GroupGeocodingForm
    queryset = SupportGroup.objects.active().all()
    success_view_name = "manage_group"


class RedirectToPresseroView(HardLoginRequiredMixin, DetailView):
    template_name = "groups/pressero_error.html"
    queryset = SupportGroup.objects.active()

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        person = request.user.person

        if not is_pressero_enabled():
            raise Http404("Cette page n'existe pas")

        if not group.is_certified:
            raise Http404("Cette page n'existe pas")

        if not Membership.objects.filter(
            supportgroup=group, person=person, is_manager=True
        ).exists:
            raise PermissionDenied("Vous ne pouvez pas accéder à cette page.")

        try:
            return redirect_to_pressero(person)
        except Exception as e:
            logger.error("Problème rencontré avec l'API Pressero", exc_info=True)

            return TemplateResponse(request, self.template_name)


class InvitationConfirmationView(VerifyLinkSignatureMixin, View):
    signature_generator = invitation_confirmation_token_generator

    def get(self, request, *args, **kwargs):
        token_params = self.get_signed_values()

        if token_params is None:
            return self.link_error_page()

        try:
            person = Person.objects.get(pk=UUID(token_params["person_id"]))
            group = SupportGroup.objects.get(pk=UUID(token_params["group_id"]))
        except (ValueError, Person.DoesNotExist):
            return self.link_error_page()
        except SupportGroup.DoesNotExist:
            messages.add_message(
                request=request,
                level=messages.ERROR,
                message="Le groupe qui vous a invité n'existe plus.",
            )
            return HttpResponseRedirect(reverse("dashboard"))

        membership, created = Membership.objects.get_or_create(
            supportgroup=group, person=person
        )

        if created:
            messages.add_message(
                request,
                messages.SUCCESS,
                format_html(
                    "Vous venez de rejoindre le groupe d'action <em>{group_name}</em>",
                    group_name=group.name,
                ),
            )
        else:
            messages.add_message(
                request, messages.INFO, "Vous étiez déjà membre de ce groupe."
            )

        return HttpResponseRedirect(reverse("view_group", args=(group.pk,)))


class InvitationWithSubscriptionView(VerifyLinkSignatureMixin, FormView):
    form_class = InvitationWithSubscriptionConfirmationForm
    signature_generator = subscription_confirmation_token_generator
    signed_params = ["email", "group_id"]
    template_name = "groups/invitation_subscription.html"

    def dispatch(self, request, *args, **kwargs):
        token_params = self.get_signed_values()

        if not token_params:
            return self.link_error_page()

        self.email = token_params["email"]

        try:
            validate_email(self.email)
        except ValidationError:
            return self.link_error_page()

        # Cas spécial : la personne s'est déjà créé un compte entretemps
        # ==> redirection vers l'autre vue
        try:
            person = Person.objects.get_by_natural_key(self.email)
        except Person.DoesNotExist:
            pass
        else:
            params = {"person_id": str(person.id), "group_id": token_params["group_id"]}
            query_params = {
                **params,
                "token": invitation_confirmation_token_generator.make_token(**params),
            }

            return HttpResponseRedirect(
                add_query_params_to_url(
                    reverse("invitation_confirmation"), query_params
                )
            )

        try:
            self.group = SupportGroup.objects.get(pk=UUID(token_params["group_id"]))
        except ValueError:
            # pas un UUID
            return self.link_error_page()
        except SupportGroup.DoesNotExist:
            # le groupe a disparu entre temps...
            self.group = None

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(group=self.group)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["group"] = self.group
        kwargs["email"] = self.email
        return kwargs

    def form_valid(self, form):
        p = form.save()
        hard_login(self.request, p)

        return TemplateResponse(self.request, "people/confirmation_subscription.html")


class InvitationAbuseReportingView(VerifyLinkSignatureMixin, View):
    signature_generator = abusive_invitation_report_token_generator
    form_template_name = "groups/invitation_abuse.html"
    confirmed_template_name = "groups/invitation_abuse_confirmed.html"

    def dispatch(self, request, *args, **kwargs):
        self.token_params = self.get_signed_values()

        if not self.token_params:
            return self.link_error_page()

        self.timestamp = abusive_invitation_report_token_generator.get_timestamp(
            request.GET.get("token")
        )

        try:
            self.group_id = UUID(self.token_params["group_id"])
            self.inviter_id = UUID(self.token_params["inviter_id"])
        except ValueError:
            return self.link_error_page()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, template=self.form_template_name)

    def post(self, request, *args, **kwargs):
        if self.inviter_id:
            send_abuse_report_message.delay(str(self.inviter_id))

        logger.info(
            msg=f"Abus d'invitation signalé ({self.group_id}, {self.inviter_id}, {self.timestamp})"
        )

        return TemplateResponse(request, template=self.confirmed_template_name)
