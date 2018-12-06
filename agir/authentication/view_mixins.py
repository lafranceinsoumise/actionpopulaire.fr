from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _


class SoftLoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path())


class HardLoginRequiredMixin(object):
    def is_authorized(self, request):
        return (
            request.user.is_authenticated
            and request.session[BACKEND_SESSION_KEY]
            != "agir.authentication.backend.MailLinkBackend"
        )

    def dispatch(self, request, *args, **kwargs):
        if self.is_authorized(request):
            return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path())


class PermissionsRequiredMixin(object):
    permissions_required = ()
    permission_denied_message = _(
        "Vous n'avez pas l'autorisation d'accéder à cette page."
    )

    def get_object(self):
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object()
        return self._cached_object

    def dispatch(self, *args, **kwargs):
        # check if there are some perms that the user does not have globally
        user = self.request.user
        local_perms = {
            perm for perm in self.permissions_required if not user.has_perm(perm)
        }

        if local_perms:
            obj = self.get_object()

            for perm in local_perms:
                if not user.has_perm(perm, obj):
                    raise PermissionDenied(self.permission_denied_message)

        return super().dispatch(*args, **kwargs)
