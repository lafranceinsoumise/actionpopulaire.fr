from django.conf import settings
from django.urls import reverse


def basic_information(request):
    logged_as = None
    profile_url = reverse("personal_information")

    if request.user.is_authenticated:
        logged_as = request.user.get_full_name()
        if not request.user.person.is_insoumise:
            profile_url = reverse("contact")

    return {
        "MAIN_DOMAIN": settings.MAIN_DOMAIN,
        "API_DOMAIN": settings.API_DOMAIN,
        "FRONT_DOMAIN": settings.FRONT_DOMAIN,
        "MAP_DOMAIN": settings.MAP_DOMAIN,
        "header_props": {
            "loggedAs": logged_as,
            "dashboardUrl": reverse("dashboard"),
            "searchUrl": reverse("search_event"),
            "helpUrl": "https://lafranceinsoumise.fr/contact/",
            "profileUrl": profile_url,
            "signInUrl": reverse("subscription"),
            "logInUrl": reverse("short_code_login"),
        },
    }
