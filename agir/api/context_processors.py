from django.conf import settings
from django.urls import reverse


def basic_information(request):
    user = None

    routes = {
        "dashboard": reverse("dashboard"),
        "search": reverse("search_event"),
        "help": "https://lafranceinsoumise.fr/contact/",
        "personalInformation": reverse("personal_information"),
        "contactConfiguration": reverse("contact"),
        "signIn": reverse("subscription"),
        "logIn": reverse("short_code_login"),
    }

    if request.user.is_authenticated:
        user = {
            "displayName": request.user.get_full_name(),
            "isInsoumise": request.user.person.is_insoumise,
        }

    return {
        "MAIN_DOMAIN": settings.MAIN_DOMAIN,
        "API_DOMAIN": settings.API_DOMAIN,
        "FRONT_DOMAIN": settings.FRONT_DOMAIN,
        "MAP_DOMAIN": settings.MAP_DOMAIN,
        "config_context": {
            "user": user,
            "routes": routes,
            "domain": settings.MAIN_DOMAIN,
        },
    }
