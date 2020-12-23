from django.conf import settings
from django.contrib import messages
from django.db.models import F
from django.middleware.csrf import get_token
from django.urls import reverse

from ..activity.actions import get_serialized_activity, get_serialized_announcements
from ..groups.models import SupportGroup


def basic_information(request):
    user = None

    routes = {
        "dashboard": reverse("dashboard"),
        "search": reverse("dashboard_search"),
        "personalInformation": reverse("personal_information"),
        "contactConfiguration": reverse("contact"),
        "join": reverse("join"),
        "login": reverse("short_code_login"),
        "createGroup": reverse("create_group"),
        "createEvent": reverse("create_event"),
        "groupsMap": reverse("carte:groups_map"),
        "groupMapPage": reverse("group_map_page"),
        "eventsMap": reverse("carte:events_map"),
        "eventMapPage": reverse("event_map_page"),
        "events": reverse("dashboard"),
        "groups": reverse("list_my_groups"),
        "activity": reverse("list_activities"),
        "required-activity": reverse("list_required_activities"),
        "menu": reverse("navigation_menu"),
        "donations": reverse("donation_amount"),
        "lafranceinsoumise": {
            "home": "https://lafranceinsoumise.fr",
            "groupMapPage": "https://lafranceinsoumise.fr/groupes-action/carte-groupes/",
            "eventMapPage": "https://lafranceinsoumise.fr/groupes-action/les-evenements-locaux/",
            "thematicTeams": reverse("thematic_teams_list"),
        },
        "noussommespour": {"home": "https://noussommespour.fr",},
        "jlmBlog": "https://melenchon.fr",
        "linsoumission": "https://linsoumission.fr",
        "feedbackForm": "https://actionpopulaire.fr/formulaires/votre-avis/",
        "help": "https://infos.actionpopulaire.fr",
        "contact": "https://infos.actionpopulaire.fr/contact/",
        "legal": "https://infos.actionpopulaire.fr/mentions-legales/",
        "nspReferral": reverse("nsp_referral"),
        "newGroupHelp": "https://infos.actionpopulaire.fr/groupes/nouvelle-equipe/",
        "groupTransferHelp": "https://infos.actionpopulaire.fr/nombre-ideal-division/",
        "charteEquipes": "https://infos.actionpopulaire.fr/charte-des-equipes-de-soutien-nous-sommes-pour/",
    }

    routes_2022 = {
        "materiel": "https://noussommespour.fr/boutique/",
        "resources": "https://noussommespour.fr/sinformer/",
        "donations": "https://noussommespour.fr/don/",
    }

    routes_insoumis = {
        "materiel": "https://materiel.lafranceinsoumise.fr/",
        "resources": "https://lafranceinsoumise.fr/fiches_pour_agir/",
        "news": "https://lafranceinsoumise.fr/actualites/",
        "thematicTeams": reverse("thematic_teams_list"),
    }

    if request.user.is_authenticated:
        routes["signOut"] = reverse("disconnect")
        person = request.user.person

        if person.is_insoumise:
            routes = {**routes, **routes_insoumis}
        elif person.is_2022:
            routes = {**routes, **routes_2022}

        user = {
            "id": person.pk,
            "firstName": person.first_name,
            "displayName": request.user.get_full_name(),
            "isInsoumise": person.is_insoumise,
            "is2022": person.is_2022,
            "isAgir": person.is_agir,
            "isGroupManager": False,
        }

        person_groups = (
            SupportGroup.objects.filter(memberships__person=person)
            .active()
            .annotate(membership_type=F("memberships__membership_type"))
            .order_by("-membership_type", "name")
        )

        if person_groups.count() > 0:
            routes["groups__personGroups"] = []
            user["groups"] = []
            for group in person_groups:
                link = {
                    "id": group.id,
                    "label": group.name,
                    "href": reverse("view_group", kwargs={"pk": group.pk}),
                }
                routes["groups__personGroups"].append(link)
                user["groups"].append(group.id)

    return {
        "MAIN_DOMAIN": settings.MAIN_DOMAIN,
        "API_DOMAIN": settings.API_DOMAIN,
        "FRONT_DOMAIN": settings.FRONT_DOMAIN,
        "MAP_DOMAIN": settings.MAP_DOMAIN,
        "global_context": {
            "user": user,
            "routes": routes,
            "csrfToken": get_token(request),
            "domain": settings.MAIN_DOMAIN,
            "activities": get_serialized_activity(request),
            "announcements": get_serialized_announcements(request),
            "toasts": [
                {"message": m.message, "html": True, "type": m.level_tag.upper()}
                for m in messages.get_messages(request)
            ],
        },
    }
