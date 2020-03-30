from django.contrib.auth import login, BACKEND_SESSION_KEY


def soft_login(request, person):
    person.ensure_role_exists()
    login(request, person.role, backend="agir.authentication.backend.MailLinkBackend")


def hard_login(request, person):
    person.ensure_role_exists()
    login(request, person.role, backend="agir.authentication.backend.ShortCodeBackend")


def is_soft_logged(request):
    return (
        request.user.is_authenticated
        and request.session[BACKEND_SESSION_KEY]
        == "agir.authentication.backend.MailLinkBackend"
    )


def is_hard_logged(request):
    return (
        request.user.is_authenticated
        and request.session[BACKEND_SESSION_KEY]
        != "agir.authentication.backend.MailLinkBackend"
    )
