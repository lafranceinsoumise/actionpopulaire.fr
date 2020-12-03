from django.conf import settings
from django.middleware.csrf import get_token
from django.urls import reverse

from ..activity.models import Activity
from ..activity.serializers import ActivitySerializer

from ..groups.models import SupportGroup


def basic_information(request):
    user = None
    activities = []

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
        "events": reverse("list_events"),
        "groups": reverse("list_my_groups"),
        "activity": reverse("list_activities"),
        "required-activity": reverse("list_required_activities"),
        "menu": reverse("navigation_menu"),
        "donations": reverse("donation_amount"),
        "lafranceinsoumise": {
            "home": "https://lafranceinsoumise.fr",
            "groupsMap": "https://lafranceinsoumise.fr/groupes-action/carte-groupes/",
            "eventsMap": "https://lafranceinsoumise.fr/groupes-action/les-evenements-locaux/",
            "thematicTeams": reverse("thematic_teams_list"),
        },
        "noussommespour": {"home": "https://noussommespour.fr",},
        "jlmBlog": "https://melenchon.fr",
        "linsoumission": "https://linsoumission.fr",
        "feedbackForm": "https://actionpopulaire.fr/formulaires/votre-avis/",
    }

    routes_2022 = {
        "materiel": "https://noussommespour.fr/boutique/",
        "help": "https://noussommespour.fr/sinformer/",
        "donations": "https://noussommespour.fr/don/",
    }

    routes_insoumis = {
        "materiel": "https://materiel.lafranceinsoumise.fr/",
        "help": "https://lafranceinsoumise.fr/fiches_pour_agir/",
        "news": "https://lafranceinsoumise.fr/actualites/",
        "contact": "https://lafranceinsoumise.fr/contact/",
        "groupMapPage": "https://lafranceinsoumise.fr/groupes-action/carte-groupes/",
        "eventMapPage": "https://lafranceinsoumise.fr/groupes-action/les-evenements-locaux/",
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
        }
        userActivities = Activity.objects.filter(recipient=person).exclude(
            status=Activity.STATUS_INTERACTED
        )
        if userActivities.count() > 0:
            activitySerializer = ActivitySerializer(
                instance=userActivities, many=True, context={"request": request}
            )
            activities = activitySerializer.data

        personGroups = SupportGroup.objects.filter(
            memberships__person=person, published=True
        ).order_by("name")
        if personGroups.count() > 0:
            routes["groups__personGroups"] = []
            user["groups"] = []
            for group in personGroups:
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
            "activities": activities,
        },
    }
