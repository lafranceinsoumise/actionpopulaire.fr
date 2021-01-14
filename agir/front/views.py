from django.conf import settings
from django.http import HttpResponsePermanentRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views.generic import View, RedirectView, TemplateView
from django.views.generic.detail import BaseDetailView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.lib.http import add_query_params_to_url
from .view_mixins import ObjectOpengraphMixin
from .view_mixins import (
    ReactBaseView,
    ReactSingleObjectView,
)
from ..events.views.event_views import EventDetailMixin
from ..groups.views.public_views import SupportGroupDetailMixin
from ..groups.serializers import SupportGroupSerializer
from ..lib.utils import generate_token_params


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


class ReactAppView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/app"


class NavigationMenuView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/app"


class ActivityView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/app"


class RequiredActivityView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/app"


class FullSupportGroupView(SoftLoginRequiredMixin, ReactSingleObjectView):
    bundle_name = "groups/fullGroupPage"
    serializer_class = SupportGroupSerializer
    queryset = SupportGroup.objects.all()

    def get_export_data(self):
        person = self.request.user.person
        person_groups = None

        if person.coordinates is not None:
            person_groups = SupportGroup.objects.active()

            if person.is_2022_only:
                person_groups = person_groups.is_2022()

            person_groups = person_groups.annotate(
                distance=Distance("coordinates", person.coordinates)
            ).order_by("distance")[:3]

            for group in person_groups:
                person_groups.membership = None

            person_groups = self.serializer_class(
                instance=person_groups, many=True, context={"request": self.request},
            ).data

        return {
            "fullGroup": self.get_serializer().data,
            "groupSuggestions": person_groups,
        }


class AgendaView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/app"


class MyGroupsView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/app"


class EventMapView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/app"


class GroupMapView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/app"


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


class JoinView(TemplateView):
    template_name = "front/join.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, type=self.request.GET.get("type"))


class EventDetailView(
    ObjectOpengraphMixin, EventDetailMixin, BaseDetailView, ReactBaseView
):
    meta_description = (
        "Participez aux événements organisés par les membres de la France insoumise."
    )
    meta_description_2022 = "Participez et organisez des événements pour soutenir la candidature de Jean-Luc Mélenchon pour 2022"
    bundle_name = "front/app"

    def get_context_data(self, **kwargs):
        kwargs["export_data"] = {"pk": self.object.pk}

        return super().get_context_data(**kwargs)


class SupportGroupDetailView(
    ObjectOpengraphMixin, SupportGroupDetailMixin, BaseDetailView, ReactBaseView
):
    meta_description = "Rejoignez les groupes d'action de la France insoumise."
    meta_description_2022 = "Rejoignez les équipes de soutien de votre quartier pour la candidature de Jean-Luc Mélenchon pour 2022"
    bundle_name = "front/app"

    def get_context_data(self, **kwargs):
        kwargs["export_data"] = {"pk": self.object.pk}

        return super().get_context_data(**kwargs)
