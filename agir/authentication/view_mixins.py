from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _

from agir.authentication.utils import is_hard_logged


class SoftLoginRequiredMixin(object):
    def is_authorized(self, request):
        # cette méthode peut être redéfinie par les classes qui intègrent ce Mixin pour spécialiser davantage
        # le mécanisme d'autorisation
        #
        # Voir par exemple :py:class:agir.donations.views.spending_requests_views.CreateSpendingRequestView
        return request.user.is_authenticated

    def dispatch(self, request, *args, **kwargs):
        if self.is_authorized(request):
            return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path())


class HardLoginRequiredMixin(SoftLoginRequiredMixin):
    def is_authorized(self, request):
        if not is_hard_logged(request):
            if not super().is_authorized(request):
                messages.add_message(
                    request,
                    messages.WARNING,
                    "Pour accéder à cette partie du site, nous devons vérifier que vous avez bien accès à votre adresse"
                    " email en vous demandant de vous reconnecter.",
                )
            return False
        return True


class PermissionsRequiredMixin(object):
    permissions_required = ()
    permission_denied_to_not_found = False
    permission_denied_message = _(
        "Vous n'avez pas l'autorisation d'accéder à cette page."
    )

    def get_object(self):
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object()
        return self._cached_object

    def get_permission_denied_response(self, object):
        if self.permission_denied_to_not_found:
            raise Http404()
        raise PermissionDenied(self.permission_denied_message)

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
                    return self.get_permission_denied_response(obj)

        return super().dispatch(*args, **kwargs)


class VerifyLinkSignatureMixin:
    signed_params = None
    signature_generator = None
    link_error_template_name = "authentication/link_error.html"

    def get_params(self):
        if self.signed_params is not None:
            return self.signed_params
        return self.signature_generator.token_params

    def get_signed_values(self):
        token = self.request.GET.get("token")
        params_keys = self.get_params()
        if (not set(params_keys) <= set(self.request.GET)) or token is None:
            return None

        params = {k: self.request.GET[k] for k in params_keys}

        if not self.signature_generator.check_token(token, **params):
            return None

        return params

    def link_error_page(self):
        return TemplateResponse(self.request, self.link_error_template_name)
