from django.conf import settings
from django.urls import reverse


def basic_information(request):
    routes = {
        "dashboard": reverse("dashboard"),
        "search": reverse("dashboard_search"),
        "personalInformation": reverse("personal_information"),
        "contactConfiguration": reverse("contact"),
        "join": reverse("join"),
        "login": reverse("short_code_login"),
        "signOut": reverse("disconnect"),
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

    return {
        "MAIN_DOMAIN": settings.MAIN_DOMAIN,
        "API_DOMAIN": settings.API_DOMAIN,
        "FRONT_DOMAIN": settings.FRONT_DOMAIN,
        "MAP_DOMAIN": settings.MAP_DOMAIN,
        "global_context": {"routes": routes, "domain": settings.MAIN_DOMAIN,},
    }
