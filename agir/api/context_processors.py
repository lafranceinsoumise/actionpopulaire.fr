from django.conf import settings
from django.middleware.csrf import get_token
from django.urls import reverse

from ..activity.models import Activity
from ..activity.serializers import ActivitySerializer


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
        "events": reverse("list_events"),
        "groups": reverse("list_my_groups"),
        "activity": reverse("list_activities"),
        "menu": reverse("navigation_menu"),
    }

    if request.user.is_authenticated:
        user = {
            "displayName": request.user.get_full_name(),
            "isInsoumise": request.user.person.is_insoumise,
        }
        person = request.user.person
        userActivities = Activity.objects.filter(recipient=person)[:20]
        if userActivities.count() > 0:
            activitySerializer = ActivitySerializer(
                instance=userActivities, many=True, context={"request": request}
            )
            activities = activitySerializer.data

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
