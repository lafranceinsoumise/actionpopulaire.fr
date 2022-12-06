import logging
from uuid import UUID

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import (
    DetailView,
    TemplateView,
    FormView,
    RedirectView,
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, ProcessFormView

from agir.authentication.tokens import (
    invitation_confirmation_token_generator,
    subscription_confirmation_token_generator,
    abusive_invitation_report_token_generator,
)
from agir.authentication.utils import hard_login
from agir.authentication.view_mixins import (
    HardLoginRequiredMixin,
    GlobalOrObjectPermissionRequiredMixin,
    VerifyLinkSignatureMixin,
)
from agir.front.view_mixins import ChangeLocationBaseView
from agir.groups.actions.pressero import is_pressero_enabled, redirect_to_pressero
from agir.groups.forms import (
    SupportGroupForm,
    GroupGeocodingForm,
    InvitationWithSubscriptionConfirmationForm,
    TransferGroupMembersForm,
)
from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.groups.tasks import (
    send_abuse_report_message,
    create_accepted_invitation_member_activity,
)
from agir.lib.export import dict_to_camelcase
from agir.lib.http import add_query_params_to_url
from agir.people.models import Person

__all__ = [
    "SupportGroupManagementView",
    "CreateSupportGroupView",
    "PerformCreateSupportGroupView",
    "RemoveManagerView",
    "ChangeGroupLocationView",
    "RedirectToPresseroView",
    "InvitationConfirmationView",
    "InvitationWithSubscriptionView",
    "InvitationAbuseReportingView",
    "TransferSupportGroupMembersView",
]


logger = logging.getLogger(__name__)


class BaseSupportGroupAdminView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, View
):
    queryset = SupportGroup.objects.active()
    permission_required = ("groups.change_supportgroup",)


class SupportGroupManagementView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        supportgroup = get_object_or_404(SupportGroup, pk=kwargs["pk"])
        active = self.request.GET.get("active", None)

        if active is None:
            return reverse("view_group_settings", kwargs={"pk": supportgroup.pk})
        if active == "informations":
            return reverse(
                "view_group_settings_general", kwargs={"pk": supportgroup.pk}
            )
        if active == "membership":
            return reverse(
                "view_group_settings_members", kwargs={"pk": supportgroup.pk}
            )
        if active == "animation":
            return reverse(
                "view_group_settings_management", kwargs={"pk": supportgroup.pk}
            )
        if active == "materiel":
            return reverse(
                "view_group_settings_materiel", kwargs={"pk": supportgroup.pk}
            )
        if active == "financement":
            return reverse(
                "view_group_settings_finance", kwargs={"pk": supportgroup.pk}
            )
        if active == "certification":
            return reverse(
                "view_group_settings_finance", kwargs={"pk": supportgroup.pk}
            )
        if active == "invitation":
            return reverse(
                "view_group_settings_members", kwargs={"pk": supportgroup.pk}
            )

        return reverse("view_group_settings", kwargs={"pk": supportgroup.pk})


class CreateSupportGroupView(HardLoginRequiredMixin, TemplateView):
    template_name = "groups/create.html"
    per_type_animation_limit = 2
    available_types = ((SupportGroup.TYPE_LOCAL_GROUP, "Groupe local"),)

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        initial = {}

        if person.contact_phone:
            initial["phone"] = person.contact_phone.as_e164

        if person.first_name and person.last_name:
            initial["name"] = "{} {}".format(person.first_name, person.last_name)

        subtypes_qs = SupportGroupSubtype.objects.filter(
            visibility=SupportGroupSubtype.VISIBILITY_ALL
        )

        types = []

        for type_id, label in self.available_types:
            disabled = self.per_type_animation_limit <= (
                SupportGroup.objects.active()
                .filter(
                    type=type_id,
                    memberships__person=person,
                    memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
                )
                .count()
            )
            types.append(
                {
                    "id": type_id,
                    "label": label,
                    "description": SupportGroup.TYPE_DESCRIPTION[type_id],
                    "disabledDescription": SupportGroup.TYPE_DISABLED_DESCRIPTION[
                        type_id
                    ],
                    "disabled": disabled,
                }
            )

        subtypes = [
            dict_to_camelcase(s.get_subtype_information())
            for s in subtypes_qs.filter(type__in=[type["id"] for type in types])
        ]

        return super().get_context_data(
            props={"initial": initial, "subtypes": subtypes, "types": types}, **kwargs
        )


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


@method_decorator(never_cache, name="get")
class TransferSupportGroupMembersView(
    BaseSupportGroupAdminView, SingleObjectMixin, FormView
):
    form_class = TransferGroupMembersForm
    template_name = "groups/transfer_group_members.html"
    permission_required = ("groups.transfer_members",)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(supportgroup=self.object)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["manager"] = self.request.user.person
        kwargs["former_group"] = self.object

        return kwargs

    def get_success_url(self):
        return "%s?active=membership" % reverse(
            "manage_group", kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        p = form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _(
                "Le transfert de %d membre(s) vers « %s » a été effectué. Ces dernier·ère·s ainsi que les animateur·ices de leur nouveau groupe ont été prévenu·es par e-mail."
            )
            % (p["transferred_memberships"].count(), p["target_group"].name),
        )

        return HttpResponseRedirect(self.get_success_url())


class RemoveManagerView(BaseSupportGroupAdminView, DetailView):
    template_name = "groups/manager_removal_confirm.html"
    queryset = (
        Membership.objects.active()
        .all()
        .select_related("supportgroup")
        .select_related("person")
    )
    permission_required = ("groups.change_membership",)

    def get_context_data(self, **kwargs):
        person = self.object.person

        if person.first_name and person.last_name:
            name = "{} {} <{}>".format(
                person.first_name, person.last_name, person.email
            )
        else:
            name = person.email

        return super().get_context_data(manager_name=name)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.membership_type = Membership.MEMBERSHIP_TYPE_MEMBER
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


class ChangeGroupLocationView(BaseSupportGroupAdminView, ChangeLocationBaseView):
    template_name = "groups/change_location.html"
    form_class = GroupGeocodingForm
    success_view_name = "view_group_settings_location"


class RedirectToPresseroView(BaseSupportGroupAdminView, DetailView):
    template_name = "groups/pressero_error.html"

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        person = request.user.person

        if not is_pressero_enabled():
            raise Http404("Cette page n'existe pas")

        if not group.is_certified:
            raise Http404("Cette page n'existe pas")

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
            create_accepted_invitation_member_activity.delay(membership.pk)
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
