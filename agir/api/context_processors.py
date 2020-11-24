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
        "help": "https://lafranceinsoumise.fr/contact/",
        "personalInformation": reverse("personal_information"),
        "contactConfiguration": reverse("contact"),
        "signIn": reverse("subscription"),
        "logIn": reverse("short_code_login"),
        "createGroup": reverse("create_group"),
        "createEvent": reverse("create_event"),
        "groupsMap": reverse("carte:groups_map"),
        "eventMap": "https://lafranceinsoumise.fr/groupes-action/les-evenements-locaux/",
        "events": reverse("list_events"),
        "groups": reverse("list_my_groups"),
        "activity": reverse("list_activities"),
        "required-activity": reverse("list_required_activities"),
        "menu": reverse("navigation_menu"),
        "thematicTeams": reverse("thematic_teams_list"),
    }

    if request.user.is_authenticated:
        person = request.user.person
        user = {
            "firstName": person.first_name,
            "displayName": request.user.get_full_name(),
            "isInsoumise": request.user.person.is_insoumise,
        }
        userActivities = Activity.objects.filter(recipient=person)
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
            for group in personGroups:
                link = {
                    "id": group.id,
                    "label": group.name,
                    "href": reverse("view_group", kwargs={"pk": group.pk}),
                }
                routes["groups__personGroups"].append(link)

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
