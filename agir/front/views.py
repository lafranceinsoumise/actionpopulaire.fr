from datetime import timedelta

from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import View

from .view_mixins import ReactListView, ReactSerializerBaseView, ReactBaseView
from ..activity.models import Activity
from ..activity.serializers import ActivitySerializer
from ..authentication.view_mixins import SoftLoginRequiredMixin
from ..events.models import Event
from ..events.serializers import EventSerializer
from ..groups.models import SupportGroup
from ..groups.serializers import SupportGroupSerializer


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


class ActivityView(SoftLoginRequiredMixin, ReactListView):
    bundle_name = "activity/activityPage"
    serializer_class = ActivitySerializer
    page_size = 20

    def get_queryset(self):
        person = self.request.user.person
        return Activity.objects.filter(recipient=person)


class AgendaView(SoftLoginRequiredMixin, ReactSerializerBaseView):
    bundle_name = "events/agendaPage"
    serializer_class = EventSerializer

    def get_export_data(self):
        person = self.request.user.person

        rsvped_events = (
            Event.objects.upcoming()
            .filter(attendees=person)
            .order_by("start_time", "end_time")
        )

        suggested_events = (
            Event.objects.upcoming()
            .exclude(rsvps__person=person)
            .filter(organizers_groups__in=person.supportgroups.all())
            .order_by("start_time")
        )

        if person.coordinates is not None and len(suggested_events) < 10:
            near_events = (
                Event.objects.upcoming()
                .filter(
                    start_time__lt=timezone.now() + timedelta(days=30),
                    do_not_list=False,
                )
                .exclude(pk__in=suggested_events)
                .exclude(rsvps__person=person)
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("distance")[: (10 - suggested_events.count())]
            )

            suggested_events = Event.objects.filter(
                Q(pk__in=suggested_events) | Q(pk__in=near_events)
            ).order_by("start_time")

        return {
            "rsvped": self.serializer_class(
                instance=rsvped_events, many=True, context={"request": self.request}
            ).data,
            "suggested": self.serializer_class(
                instance=suggested_events, many=True, context={"request": self.request}
            ).data,
        }


class MyGroupsView(SoftLoginRequiredMixin, ReactListView):
    serializer_class = SupportGroupSerializer
    bundle_name = "groups/groupsPage"
    data_script_id = "mes-groupes"

    def get_queryset(self):
        return SupportGroup.objects.filter(memberships__person=self.request.user.person)
