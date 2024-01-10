from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import RedirectView
from oauth2_provider.views import AuthorizationView

from agir.authentication.view_mixins import HardLoginRequiredMixin

__all__ = [
    "RedirectToMixin",
    "Oauth2AuthorizationView",
    "SocialLoginError",
]


class RedirectToMixin:
    redirect_field_name = REDIRECT_FIELD_NAME

    def dispatch(self, request, *args, **kwargs):
        params = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, None),
        )

        if params is not None:
            self.request.session[self.redirect_field_name] = params
        elif self.redirect_field_name in self.request.session:
            del self.request.session[self.redirect_field_name]

        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.session.get(self.redirect_field_name, "")

        # we first strip to remove potential trailing slash, then rsplit and take last component to remove
        # http:// or https://
        allowed_hosts = {
            s.strip("/").rsplit("/", 1)[-1]
            for s in [settings.MAIN_DOMAIN, settings.API_DOMAIN, settings.FRONT_DOMAIN]
        }
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=allowed_hosts,
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ""


class Oauth2AuthorizationView(HardLoginRequiredMixin, AuthorizationView):
    pass


class SocialLoginError(RedirectView):
    url = reverse_lazy("short_code_login")

    def get(self, request, *args, **kwargs):
        if self.request.GET.get("message"):
            messages.add_message(
                request=request,
                level=messages.ERROR,
                message="Une erreur inconnue est survenue lors de votre tentative de connexion."
                " Veuillez vous connecter autrement ou réessayer plus tard.",
            )

        return super().get(request, *args, **kwargs)
