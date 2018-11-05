from django.contrib.auth import login


def soft_login(request, person):
    login(request, person.role, backend='agir.authentication.backend.MailLinkBackend')


def hard_login(request, person):
    login(request, person.role, backend='agir.authentication.backend.ShortCodeBackend')
