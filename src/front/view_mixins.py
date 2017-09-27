from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseForbidden


class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url=reverse_lazy('oauth_redirect_view')), )
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PermissionsRequiredMixin(object):
    permissions_required = ()

    def dispatch(self, *args, **kwargs):
        # check if there are some perms that the user does not have globally
        user = self.request.user
        local_perms = {perm for perm in self.permissions_required if not user.has_perm(perm)}

        if local_perms:
            obj = self.get_object()

            for perm in local_perms:
                if not user.has_perm(perm, obj):
                    return HttpResponseForbidden(b'Not allowed')

        return super().dispatch(*args, **kwargs)
