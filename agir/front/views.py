from datetime import timedelta

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F, Q
from django.http import HttpResponsePermanentRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import View, RedirectView, TemplateView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.events.models import Event
from agir.events.serializers import EventSerializer
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupSerializer
from agir.lib.http import add_query_params_to_url
from agir.lib.tasks import geocode_person
from .view_mixins import ReactListView, ReactSerializerBaseView, ReactBaseView
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
        event = Event.objects.filter(
            nb_path=nb_path, visibility=Event.VISIBILITY_PUBLIC
        ).first()
        if event:
            return HttpResponsePermanentRedirect(reverse("view_event", args=[event.id]))

        group = SupportGroup.objects.filter(nb_path=nb_path, published=True).first()
        if group:
            return HttpResponsePermanentRedirect(reverse("view_group", args=[group.id]))

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


class NavigationMenuView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "front/navigationPage"


class ActivityView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "activity/page__activities"


class RequiredActivityView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "activity/page__requiredActivities"


class AgendaView(SoftLoginRequiredMixin, ReactSerializerBaseView):
    bundle_name = "events/agendaPage"
    serializer_class = EventSerializer

    def get(self, request, *args, **kwargs):
        person = request.user.person

        if person.coordinates_type is None:
            geocode_person.delay(person.pk)

        return super().get(request, *args, **kwargs)

    def get_export_data(self):
        person = self.request.user.person
        queryset = Event.objects.with_serializer_prefetch(person)
        if person.is_2022_only:
            queryset = queryset.is_2022()

        rsvped_events = (
            queryset.upcoming()
            .filter(Q(attendees=person) | Q(organizers=person))
            .order_by("start_time", "end_time")
        ).distinct()

        groups_events = (
            queryset.upcoming()
            .filter(organizers_groups__in=person.supportgroups.all())
            .distinct()
        )

        organized_events = (
            queryset.past()
            .filter(organizers=person)
            .distinct()
            .order_by("-start_time")[:10]
        )

        past_events = (
            queryset.past()
            .filter(
                Q(rsvps__person=person)
                | Q(organizers_groups__in=person.supportgroups.all())
            )
            .distinct()
            .order_by("-start_time")[:10]
        )

        other_events = groups_events.union(organized_events, past_events)

        if person.coordinates is not None:
            near_events = (
                queryset.upcoming()
                .filter(
                    start_time__lt=timezone.now() + timedelta(days=30),
                    do_not_list=False,
                )
                .exclude(pk__in=groups_events)
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("distance")[:10]
            )

            other_events = (
                queryset.filter(
                    pk__in=[e.pk for e in near_events] + [e.pk for e in other_events]
                )
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("start_time")
                .distinct()
            )
        else:
            other_events = other_events.order_by("start_time")

        fields = [
            "id",
            "name",
            "participantCount",
            "illustration",
            "hasSubscriptionForm",
            "startTime",
            "endTime",
            "location",
            "isOrganizer",
            "rsvp",
            "canRSVP",
            "is2022",
            "routes",
            "groups",
            "distance",
            "compteRendu",
        ]

        return {
            "rsvped": self.serializer_class(
                instance=rsvped_events,
                many=True,
                context={"request": self.request},
                fields=fields,
            ).data,
            "others": self.serializer_class(
                instance=other_events,
                many=True,
                context={"request": self.request},
                fields=fields,
            ).data,
        }


class MyGroupsView(SoftLoginRequiredMixin, ReactListView):
    serializer_class = SupportGroupSerializer
    bundle_name = "groups/groupsPage"
    data_script_id = "mes-groupes"

    def get_queryset(self):
        person = self.request.user.person
        person_groups = (
            SupportGroup.objects.filter(memberships__person=self.request.user.person)
            .active()
            .annotate(membership_type=F("memberships__membership_type"))
            .order_by("-membership_type", "name")
        )
        if person_groups.count() == 0 and person.coordinates is not None:
            person_groups = SupportGroup.objects.active()
            if person.is_2022_only:
                person_groups = person_groups.is_2022()
            person_groups = person_groups.annotate(
                distance=Distance("coordinates", person.coordinates)
            ).order_by("distance")[:3]
            for group in person_groups:
                person_groups.membership = None

        return person_groups


class EventMapView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "carte/page__eventMap"


class GroupMapView(SoftLoginRequiredMixin, ReactBaseView):
    bundle_name = "carte/page__groupMap"


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
