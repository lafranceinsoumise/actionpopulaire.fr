from django.conf import settings
from django.contrib.auth import login, BACKEND_SESSION_KEY
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


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


def valid_emails(candidate_emails):
    for email in candidate_emails:
        try:
            validate_email(email)
            yield email
        except ValidationError:
            pass


def get_bookmarked_emails(request):
    if "knownEmails" not in request.COOKIES:
        return []
    candidate_emails = request.COOKIES.get("knownEmails").split(",")
    return list(valid_emails(candidate_emails))


def bookmark_email(email, request, response):
    domain = ".".join(request.META.get("HTTP_HOST", "").split(":")[0].split(".")[-2:])
    emails = get_bookmarked_emails(request)

    if email in emails:
        emails.remove(email)

    emails.insert(0, email)

    response.set_cookie(
        "knownEmails",
        value=",".join(emails[0:4]),
        max_age=365 * 24 * 3600,
        domain=domain,
        secure=not settings.DEBUG,
        httponly=True,
    )

    return response
