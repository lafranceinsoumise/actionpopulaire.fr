from django.contrib.auth import (
    user_logged_in,
    BACKEND_SESSION_KEY,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

import agir.authentication
from agir.authentication import metrics


@receiver(user_logged_in, dispatch_uid="user_logged_in_count")
def user_logged_in_count(request, **kwargs):
    metrics.logged_in.labels(backend=request.session[BACKEND_SESSION_KEY]).inc()


@receiver(user_logged_out, dispatch_uid="user_logged_out_count")
def user_logged_out_count(request, **kwargs):
    metrics.logged_out.inc()


@receiver(user_login_failed, dispatch_uid="user_login_failed_count")
def user_login_failed_count(credentials, **kwargs):
    backend = None
    if "short_code" in credentials:
        backend = "agir.authentication.backend.ShortCodeBackend"
    if "user_pk" in credentials and "token" in credentials:
        backend = "agir.authentication.backend.MailLinkBackend"

    if backend is not None:
        agir.authentication.metrics.login_failed.labels(backend).inc()
