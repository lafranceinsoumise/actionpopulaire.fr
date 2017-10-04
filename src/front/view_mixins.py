from django.contrib.auth import BACKEND_SESSION_KEY, authenticate, login
from django.contrib.auth.views import redirect_to_login
from django.http.response import HttpResponseForbidden


class SoftLoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        elif 'p' in request.GET and 'code' in request.GET:
            user = authenticate(user_pk=request.GET['p'], code=request.GET['code'])

            if user:
                login(request, user)
                return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path(), 'oauth_redirect_view')


class HardLoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.session[BACKEND_SESSION_KEY] != 'front.backend.MailLinkBackend':
            return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path(), 'oauth_redirect_view')


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


class SimpleOpengraphMixin():
    meta_title = None
    meta_description = None
    meta_type = 'article'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            show_opengraph=True,
            meta_title=self.get_meta_title(),
            meta_description=self.get_meta_description(),
            meta_type=self.meta_type,
            **kwargs
        )

    def get_meta_title(self):
        return self.meta_title

    def get_meta_description(self):
        return self.meta_description


class ObjectOpengraphMixin(SimpleOpengraphMixin):
    title_prefix = None

    def get_meta_title(self):
        return '{} - {}'.format(self.title_prefix, self.object.name)
