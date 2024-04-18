import os
from urllib.parse import urljoin

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import (
    HttpResponsePermanentRedirect,
    Http404,
    FileResponse,
    HttpResponseRedirect,
)
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators import cache
from django.views.generic import View, RedirectView, TemplateView
from django.views.generic.detail import BaseDetailView

from agir.api.context_processors import basic_information
from agir.authentication.view_mixins import (
    HardLoginRequiredMixin,
    SoftLoginRequiredMixin,
    GlobalOrObjectPermissionRequiredMixin,
)
from agir.donations.actions import (
    can_make_contribution,
    get_active_contribution_for_person,
    is_waiting_contribution,
)
from agir.donations.models import SpendingRequest
from agir.events.models import EventSubtype
from agir.events.views.event_views import EventDetailMixin
from agir.front.view_mixins import (
    ReactBaseView,
    SimpleOpengraphMixin,
    ObjectOpengraphMixin,
)
from agir.groups.models import SupportGroupSubtype
from agir.groups.views.public_views import SupportGroupDetailMixin
from agir.lib.http import add_query_params_to_url
from agir.lib.mailing import get_context_from_bindings
from agir.lib.utils import generate_token_params, front_url
from agir.msgs.models import SupportGroupMessage
from agir.people.models import Person

cache_decorators = [cache.cache_page(30), cache.cache_control(public=True)]


class BasicOpenGraphMixin(SimpleOpengraphMixin):
    meta_title = "Action Populaire"
    meta_description = (
        "Action Populaire est le réseau social d'action de la France insoumise."
    )
    meta_type = "website"
    meta_image = urljoin(settings.FRONT_DOMAIN, static("front/assets/og_image_NSP.jpg"))


## BASE VIEWS


class BaseAppView(BasicOpenGraphMixin, ReactBaseView):
    pass


@method_decorator(cache_decorators, name="get")
class BaseAppCachedView(BaseAppView):
    pass


class BaseAppSoftAuthView(SoftLoginRequiredMixin, BaseAppView):
    pass


class BaseAppHardAuthView(HardLoginRequiredMixin, BaseAppView):
    pass


class NotFoundView(BaseAppView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response.status_code = 404
        return response


class ServiceWorker(View):
    def get(self, *args, **kwargs):
        return FileResponse(
            open(
                os.path.join(
                    os.path.dirname(settings.BASE_DIR),
                    "assets",
                    "components",
                    "service-worker.js",
                ),
                "rb",
            )
        )


## TEST_VIEWS


class LayoutCssTestView(TemplateView):
    template_name = "front/layout_css_test.html"


class ReactCssTestView(BaseAppCachedView):
    template_name = "front/react_view_css_test.html"


class EmailTestView(BaseAppCachedView):
    def get_template_names(self):
        try:
            template_name = self.kwargs.get("template")
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        recipient = Person.objects.get_by_natural_key(email=settings.EMAIL_SUPPORT)
        context = get_context_from_bindings(None, recipient, self.request.GET.dict())
        kwargs.update(context)
        kwargs.update(basic_information(None))
        kwargs["email_template"] = "mail_templates/layout.html"

        return super().get_context_data(**kwargs)


class FontAwesomeTestView(BaseAppCachedView):
    def get_used_icons(self):
        event = EventSubtype.objects.filter(icon_name__isnull=False).values_list(
            "icon_name", flat=True
        )
        group = SupportGroupSubtype.objects.filter(icon_name__isnull=False).values_list(
            "icon_name", flat=True
        )
        return list(set(event) | set(group))

    def get_context_data(self, **kwargs):
        kwargs.setdefault("export_data", self.get_used_icons())
        kwargs.setdefault("data_script_id", "usedIcons")
        return super().get_context_data(**kwargs)


## AUTH VIEWS


class SignupView(BaseAppCachedView):
    meta_title = "Inscription"
    meta_description = "Rejoignez Action Populaire"


class CodeSignupView(BaseAppCachedView):
    meta_title = "Inscription"
    meta_description = "Rejoignez Action Populaire"


class LoginView(BaseAppCachedView):
    meta_title = "Connexion"
    meta_description = "Connectez-vous à Action Populaire"

    def get_meta_title(self):
        default = super().get_meta_title()
        if "meta_title" in self.request.GET:
            return self.request.GET.get("meta_title", default)
        return default

    def get_meta_description(self):
        default = super().get_meta_title()
        if "meta_description" in self.request.GET:
            return self.request.GET.get("meta_description", default)
        return default

    def get_meta_image(self):
        default = super().get_meta_title()
        if "meta_image" in self.request.GET:
            return self.request.GET.get("meta_image", default)
        return default


class CodeLoginView(BaseAppCachedView):
    meta_title = "Connexion"
    meta_description = "Connectez-vous à Action Populaire"


class LogoutView(BaseAppView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


## DASHBOARD VIEWS


class HomepageView(BaseAppCachedView):
    def get_api_preloads(self):
        if self.request.user.is_authenticated and self.request.user.person:
            return [
                reverse_lazy("api_grand_events"),
                reverse_lazy("api_event_rsvped"),
                reverse_lazy("api_event_suggestions"),
            ]
        return []


class UserSupportGroupsView(BaseAppSoftAuthView):
    def get_api_preloads(self):
        if self.request.user.person.supportgroups.active().exists():
            return [reverse_lazy("api_user_groups")]
        return [reverse_lazy("api_user_group_suggestions")]


class ThematicGroupsView(BaseAppCachedView):
    meta_title = "Les groupes thématiques de l'espace programme - La France insoumise"
    meta_image = urljoin(
        settings.FRONT_DOMAIN, static("front/images/thematic_groups.jpg")
    )

    def get_api_preloads(self):
        return [*super().get_api_preloads(), reverse_lazy("api_thematic_groups")]


class UserMessagesView(BaseAppHardAuthView):
    def get_api_preloads(self):
        return [f"{reverse_lazy('api_user_messages')}?page=1&page_size=10"]


class UserMessageView(
    BaseAppHardAuthView,
    GlobalOrObjectPermissionRequiredMixin,
):
    permission_required = ("msgs.view_supportgroupmessage",)
    queryset = SupportGroupMessage.objects.active()

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("user_messages"))

        return super().handle_no_permission()

    def get_api_preloads(self):
        return super().get_api_preloads() + [
            f"{reverse_lazy('api_user_messages')}?page=1&page_size=10",
            reverse_lazy("api_group_message_detail", kwargs=self.kwargs),
        ]


class GroupMessageRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, pk=None, message_pk=None, **kwargs):
        return front_url("user_message_details", kwargs={"pk": message_pk})


## DONATION VIEWS


class DonationView(BaseAppCachedView):
    meta_title = "Faire un don - La France insoumise"
    meta_description = (
        "Pour financer les dépenses liées à l’organisation d’événements, à l’achat de matériel, au"
        "fonctionnement du site, etc., nous avons besoin du soutien financier de chacun.e d’entre vous !"
    )


class AlreadyContributorRedirectView(RedirectView):
    query_string = False
    message = None

    @property
    def url(self):
        active_contribution = None

        if (
            self.request.user.is_authenticated
            and hasattr(self.request.user, "person")
            and self.request.user.person is not None
        ):
            active_contribution = get_active_contribution_for_person(
                person=self.request.user.person
            )

            if active_contribution and is_waiting_contribution(active_contribution):
                self.message = (
                    "Vous avez déjà effectuée une contribution financière pour cette année : il ne vous reste à "
                    "présent qu'à en valider le paiement pour que celle-ci soit effective."
                )
                return reverse("payment_page", args=(active_contribution.pk,))

        if active_contribution:
            self.message = mark_safe(
                "Vous avez déjà effectuée une contribution financière pour cette année ! "
                "Merci de votre soutien ! Si vous le souhaitez vous pouvez toujours faire un don ponctuel "
                f'<a href="{front_url("donation_amount", absolute=True)}">sur la page de don</a>.'
            )

        return reverse("view_payments")

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.message:
            messages.add_message(
                request=self.request, level=messages.WARNING, message=self.message
            )
        return response


class ContributionView(BaseAppCachedView):
    meta_title = "Devenir financeur·euse de la France insoumise"
    meta_image = urljoin(
        settings.FRONT_DOMAIN, static("front/og-image/contributions.png")
    )
    meta_description = (
        "Pour financer les dépenses liées à l’organisation d’événements, à l’achat de matériel, au"
        "fonctionnement du site, etc., nous avons besoin du soutien financier de chacun.e d’entre vous !"
    )

    restricted = True

    def get(self, request, *args, **kwargs):
        if (
            self.restricted
            and request.user.is_authenticated
            and hasattr(request.user, "person")
            and request.user.person is not None
            and not can_make_contribution(person=request.user.person)
        ):
            return HttpResponseRedirect(reverse_lazy("already_contributor"))

        return super().get(request, *args, **kwargs)


class ContributionRenewalView(BaseAppHardAuthView):
    meta_title = "renouveler le financement à la France insoumise"
    meta_image = urljoin(
        settings.FRONT_DOMAIN, static("front/og-image/contributions.png")
    )
    meta_description = (
        "Pour financer les dépenses liées à l’organisation d’événements, à l’achat de matériel, au"
        "fonctionnement du site, etc., nous avons besoin du soutien financier de chacun.e d’entre vous !"
    )

    def get_api_preloads(self):
        return [reverse_lazy("api_active_contribution_retrieve")]

    def get(self, request, *args, **kwargs):
        if not can_make_contribution(person=request.user.person):
            return HttpResponseRedirect(reverse_lazy("already_contributor"))

        return super().get(request, *args, **kwargs)


class Donation2022View(DonationView):
    meta_title = "Faire un don - Mélenchon 2022"


class SupportGroupDonationView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, pk=None, **kwargs):
        return front_url("donation_amount", query={"group": pk})


class SupportGroupContributionView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, pk=None, **kwargs):
        return front_url("contribution_amount", query={"group": pk})


## EVENT VIEWS


class EventDetailView(
    EventDetailMixin, BaseDetailView, ObjectOpengraphMixin, ReactBaseView
):
    meta_description = "Participez et organisez des événements pour soutenir les propositions de la France insoumise"

    def get_api_preloads(self):
        return [reverse_lazy("api_event_details", kwargs=self.kwargs)]

    def get_meta_image(self):
        return self.object.get_meta_image()

    def get_page_schema(self):
        return self.object.get_page_schema()


class EventSettingsView(HardLoginRequiredMixin, EventDetailView):
    pass


class EventProjectView(HardLoginRequiredMixin, EventDetailView):
    def get_api_preloads(self):
        return [
            reverse_lazy("api_event_details", kwargs=self.kwargs),
            reverse_lazy("api_event_project", kwargs={"event_id": self.kwargs["pk"]}),
        ]


class CreateEventView(BaseAppSoftAuthView):
    api_preloads = [reverse_lazy("api_event_create_options")]


class GroupUpcomingEventsView(BaseAppSoftAuthView):
    api_preloads = [reverse_lazy("api_group_upcoming_events")]


class GroupUpcomingEventsForGroupView(BaseAppSoftAuthView):
    def get_api_preloads(self):
        return [
            reverse_lazy("api_group_view", kwargs=self.kwargs),
        ]


## SEARCH VIEW


class SearchView(BaseAppCachedView):
    meta_title = "Rechercher"
    meta_description = "Rechercher un groupe, un événement"


## SUPPORTGROUP VIEWS


class SupportGroupDetailView(
    SupportGroupDetailMixin, BaseDetailView, ObjectOpengraphMixin, ReactBaseView
):
    meta_description = "Rejoignez les groupes d'action de votre quartier pour soutenir les propositions de la France insoumise"

    def get_api_preloads(self):
        return [
            reverse_lazy("api_group_view", kwargs=self.kwargs),
            reverse_lazy("api_near_groups_view", kwargs=self.kwargs),
        ]

    def get_meta_image(self):
        return self.object.get_meta_image()


class SupportGroupSettingsView(HardLoginRequiredMixin, SupportGroupDetailView):
    permission_required = ("groups.change_supportgroup",)


class CreateSupportGroupSpendingRequestView(
    HardLoginRequiredMixin, SupportGroupDetailView
):
    permission_required = ("donations.add_spendingrequest",)

    def get_api_preloads(self):
        return [
            reverse_lazy("api_group_view", kwargs=self.kwargs),
        ]

    def get_meta_image(self):
        return self.object.get_meta_image()


## SPENDING REQUEST VIEW


class SpendingRequestDetailsView(
    HardLoginRequiredMixin,
    GlobalOrObjectPermissionRequiredMixin,
    BaseDetailView,
    ReactBaseView,
):
    model = SpendingRequest
    permission_required = ("donations.view_spendingrequest",)

    def get_api_preloads(self):
        return [
            reverse_lazy(
                "api_spending_request_retrieve_update_delete", kwargs=self.kwargs
            ),
        ]


class SpendingRequestUpdateView(SpendingRequestDetailsView):
    permission_required = ("donations.change_spendingrequest",)

    def handle_no_permission(self):
        if self.get_object().editable:
            return super().handle_no_permission()

        messages.add_message(
            self.request,
            messages.WARNING,
            "Cette demande ne peut pas être modifiée",
        )
        return HttpResponseRedirect(
            reverse("spending_request_details", kwargs=self.kwargs)
        )


class VotingProxyView(BaseAppCachedView):
    meta_title = "Se porter volontaire pour voter par procuration - Action Populaire"
    meta_description = (
        "Prenez une procuration près de chez vous, pour voter pour les candidats-es de l'Union Populaire "
        "aux élections européennes du 9 juin 2024."
    )
    meta_type = "website"
    meta_image = urljoin(settings.FRONT_DOMAIN, static("front/assets/og_image_vp.jpg"))


class ReplyToSingleVotingProxyRequestView(BaseAppSoftAuthView):
    meta_title = "Se porter volontaire pour voter par procuration - Action Populaire"
    meta_description = (
        "Prenez une procuration près de chez vous, pour voter pour les candidats-es de l'Union Populaire "
        "aux élections européennes du 9 juin 2024."
    )
    meta_type = "website"
    meta_image = urljoin(settings.FRONT_DOMAIN, static("front/assets/og_image_vp.jpg"))


class VotingProxyRequestView(BaseAppCachedView):
    meta_title = "Voter par procuration — Action Populaire"
    meta_description = (
        "Faites la demande qu'un·e volontaire de votre ville vote à votre place pour les candidats-es de "
        "l'Union Populaire aux élections européennes du 9 juin 2024."
    )
    meta_type = "website"
    meta_image = urljoin(settings.FRONT_DOMAIN, static("front/assets/og_image_vpr.jpg"))


class PollingStationOfficerView(BaseAppCachedView):
    meta_title = "Devenir assesseur·e ou délégué·e — Action Populaire"
    meta_description = (
        "Pour la réussite de ce scrutin, il est nécessaire que nous ayons un maximum d'assesseur⋅es "
        "et de délégué⋅es dans le plus grand nombre de bureaux de vote de la circonscription."
    )
    meta_type = "website"
    meta_image = urljoin(settings.FRONT_DOMAIN, static("front/assets/og_image_pso.jpg"))


class EventSpeakerView(SoftLoginRequiredMixin, ReactBaseView):
    api_preloads = [
        reverse_lazy("api_event_speaker_retrieve_update"),
        reverse_lazy("api_event_speaker_event_list"),
    ]


## REDIRECT / EXTERNAL VIEWS


class NBUrlsView(View):
    nb_paths = {
        "/unsubscribe": reverse_lazy("unsubscribe"),
        "/inscription": reverse_lazy("subscription_overseas"),
        "/login": reverse_lazy("short_code_login"),
        "/users/event_pages/new?parent_id=103": reverse_lazy("create_event"),
        "/users/event_pages/new?parent_id=73": reverse_lazy("create_group"),
        "/users/event_pages/new?parent_id=38840": reverse_lazy("create_event"),
        "/agir": reverse_lazy("volunteer"),
        "/inscription_detail": reverse_lazy("personal_information"),
        "/projet": "https://avenirencommun.fr/avenir-en-commun/",
        "/le_projet": "https://avenirencommun.fr/avenir-en-commun/",
        "/livrets_thematiques": "https://avenirencommun.fr/livrets-thematiques/",
        "/convention": "https://convention.jlm2017.fr/",
        "/commander_du_materiel": "https://materiel.lafranceinsoumise.fr/",
        "/materiel": "https://materiel.lafranceinsoumise.fr/",
        "/actualites": "https://lafranceinsoumise.fr/actualites/",
        "/le_blog": "http://melenchon.fr/",
        "/donner": "https://dons.lafranceinsoumise.fr/",
        "/groupes_appui": "https://lafranceinsoumise.fr/carte",
        "/groupes_d_appui": "https://lafranceinsoumise.fr/carte",
        "/groupes_appui_redirige": "https://lafranceinsoumise.fr/carte",
        "/evenements_locaux_redirige": "https://lafranceinsoumise.fr/carte",
        "/evenements_locaux": "https://lafranceinsoumise.fr/carte",
        "/les_groupes_d_appui": "https://lafranceinsoumise.fr/carte",
        "/creer_ou_rejoindre_un_groupe_d_appui": "https://lafranceinsoumise.fr/carte",
        "/actualites-groupes-appui": "https://lafranceinsoumise.fr/category/actualites-groupes-appui/",
        "/groupes_proches": "https://lafranceinsoumise.fr/groupes-appui/carte-groupes-dappui/",
        "/evenements_proches": "https://lafranceinsoumise.fr/groupes-appui/carte-groupes-dappui/",
        "/caravanes_liste": "https://lafranceinsoumise.fr/groupes-appui/les-casserolades/",
        "/carte": "https://lafranceinsoumise.fr/carte",
        "/merci": "https://lafranceinsoumise.fr/merci",
        "/18_mrs": "https://18mars2017.fr/",
        "/universites_populaires": "https://avenirencommun.fr/univpop_programme/",
        "/agenda_melenchon": "https://agir.lafranceinsoumise.fr/agenda/melenchon/",
    }

    def get(self, request, nb_path):
        try:
            nb_url = nb_path
            if request.META["QUERY_STRING"]:
                nb_url = nb_url + "?" + request.META["QUERY_STRING"]
                try:
                    url = self.nb_paths[nb_url]
                    return HttpResponsePermanentRedirect(url)
                except KeyError:
                    pass
            url = self.nb_paths[nb_path]
            return HttpResponsePermanentRedirect(url)
        except KeyError:
            pass

        raise Http404()


class NSPView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = settings.NSP_DOMAIN
        if self.request.user.is_authenticated:
            person = self.request.user.person
            if person.is_2022:
                return url
            url = add_query_params_to_url(
                url,
                {
                    "prenom": person.first_name,
                    "nom": person.last_name,
                    "email": person.email,
                    "phone": person.contact_phone,
                    "zipcode": person.location_zip,
                },
            )

        return url


class NSPReferralView(SoftLoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = f"{settings.NSP_DOMAIN}/je-partage-mon-lien/"

        params = generate_token_params(self.request.user.person)
        params["_p"] = params.pop("p")

        # copier les paramètres UTM
        params.update(
            {k: v for k, v in self.request.GET.items() if k.startswith("utm_")}
        )

        url = add_query_params_to_url(url, params)
        return url


class PostElectionRedirectView(RedirectView):
    query_string = False
    url = reverse_lazy("dashboard")

    def get(self, request, *args, **kwargs):
        messages.add_message(
            request=request,
            level=messages.WARNING,
            message="La page du lien que vous avez ouvert n'existe plus. Merci de votre soutien !",
        )
        return super().get(request, *args, **kwargs)
