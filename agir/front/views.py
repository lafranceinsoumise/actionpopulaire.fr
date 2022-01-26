import os

from django.conf import settings
from django.contrib.auth import logout
from django.http import (
    HttpResponsePermanentRedirect,
    Http404,
    FileResponse,
)
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators import cache
from django.views.generic import View, RedirectView
from django.views.generic.detail import BaseDetailView

from agir.authentication.view_mixins import (
    HardLoginRequiredMixin,
    SoftLoginRequiredMixin,
    GlobalOrObjectPermissionRequiredMixin,
)
from agir.lib.http import add_query_params_to_url
from .view_mixins import (
    ReactBaseView,
    SimpleOpengraphMixin,
    ObjectOpengraphMixin,
)
from ..events.views.event_views import EventDetailMixin
from ..groups.views.public_views import SupportGroupDetailMixin
from ..lib.utils import generate_token_params
from ..msgs.models import SupportGroupMessage

cache_decorators = [cache.cache_page(30), cache.cache_control(public=True)]


class BasicOpenGraphMixin(SimpleOpengraphMixin):
    meta_title = "Action Populaire"
    meta_description = (
        "Action Populaire est le réseau social d'action de la campagne de Jean-Luc Mélenchon pour "
        "l'élection présidentielle de 2022. "
    )
    meta_type = "website"
    meta_image = static("front/assets/og_image_NSP.jpg")


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
                reverse_lazy("api_event_rsvped"),
                reverse_lazy("api_event_suggestions"),
            ]
        return []


class UserSupportGroupsView(BaseAppSoftAuthView):
    api_preloads = [reverse_lazy("api_user_groups")]


class UserMessagesView(BaseAppHardAuthView):
    api_preloads = [reverse_lazy("api_user_messages")]


class UserMessageView(
    GlobalOrObjectPermissionRequiredMixin,
    UserMessagesView,
):
    permission_required = ("msgs.view_supportgroupmessage",)

    queryset = SupportGroupMessage.objects.active()

    def get_object(self):
        return get_object_or_404(self.queryset, pk=self.kwargs.get("pk"))

    def get_api_preloads(self):
        return super().get_api_preloads() + [
            reverse_lazy("api_group_message_detail", kwargs=self.kwargs)
        ]


## DONATION VIEWS


class DonationView(BaseAppCachedView):
    meta_title = "Faire un don - La France insoumise"
    meta_description = (
        "Pour financer les dépenses liées à l’organisation d’événements, à l’achat de matériel, au"
        "fonctionnement du site, etc., nous avons besoin du soutien financier de chacun.e d’entre vous !"
    )


class Donation2022View(DonationView):
    meta_title = "Faire un don - Mélenchon 2022"


## EVENT VIEWS


class EventDetailView(
    EventDetailMixin, BaseDetailView, ObjectOpengraphMixin, ReactBaseView
):
    meta_description = "Participez et organisez des événements pour soutenir la candidature de Jean-Luc Mélenchon pour 2022"

    def get_api_preloads(self):
        return [reverse_lazy("api_event_view", kwargs=self.kwargs)]

    def get_meta_image(self):
        return self.object.get_meta_image()


class EventSettingsView(HardLoginRequiredMixin, EventDetailView):
    permission_required = "event.change_event"


class EventProjectView(HardLoginRequiredMixin, EventDetailView):
    permission_required = "event.change_event"

    def get_api_preloads(self):
        return [
            reverse_lazy("api_event_view", kwargs=self.kwargs),
            reverse_lazy("api_event_project", kwargs={"event_id": self.kwargs["pk"]}),
        ]


class CreateEventView(BaseAppSoftAuthView):
    api_preloads = [reverse_lazy("api_event_create_options")]


## SUPPORTGROUP VIEWS


class SupportGroupDetailView(
    SupportGroupDetailMixin, BaseDetailView, ObjectOpengraphMixin, ReactBaseView
):
    meta_description = "Rejoignez les groupes d'action de votre quartier pour la candidature de Jean-Luc Mélenchon pour 2022"

    def get_api_preloads(self):
        return [
            reverse_lazy("api_group_view", kwargs=self.kwargs),
            reverse_lazy("api_near_groups_view", kwargs=self.kwargs),
        ]

    def get_meta_image(self):
        return self.object.get_meta_image()


class SupportGroupSettingsView(HardLoginRequiredMixin, SupportGroupDetailView):
    permission_required = "groups.change_supportgroup"


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


class VotingProxyView(BaseAppCachedView):
    meta_title = "Se porter volontaire - Procurations Mélenchon 2022 - Action Populaire"
    meta_description = (
        "Prenez la procuration d'un·e soutien de Jean-Luc Mélenchon dans votre ville, pour voter pour "
        "l'élection présidentielle le 10 et/ou 24 avril 2022."
    )
    meta_type = "website"
    meta_image = static("front/assets/og_image_vp.jpg")


class VotingProxyRequestView(BaseAppCachedView):
    meta_title = "Voter par procuration pour Jean-Luc Mélenchon — Action Populaire"
    meta_description = (
        "Faites la demande qu'un·e volontaire de votre ville vote à votre place pour Jean-Luc "
        "Mélenchon pour l'élection présidentielle du 10 et/ou 24 avril 2022."
    )
    meta_type = "website"
    meta_image = static("front/assets/og_image_vpr.jpg")
