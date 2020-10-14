from django.conf import settings
from django.urls import reverse


def basic_information(request):
    return {
        "MAIN_DOMAIN": settings.MAIN_DOMAIN,
        "API_DOMAIN": settings.API_DOMAIN,
        "FRONT_DOMAIN": settings.FRONT_DOMAIN,
        "MAP_DOMAIN": settings.MAP_DOMAIN,
        "header_props": {
            "loggedAs": request.user.get_full_name(),
            "dashboardUrl": reverse("dashboard"),
            "searchUrl": reverse("search_event"),
            "helpUrl": "#",
            "profileUrl": reverse("personal_information"),
            "signInUrl": reverse("subscription"),
            "logInUrl": reverse("short_code_login"),
        },
    }
