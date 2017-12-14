from urllib.parse import urljoin

from django.contrib.auth import BACKEND_SESSION_KEY, authenticate, login
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.html import format_html
from django.shortcuts import reverse
from django.views.generic import UpdateView, ListView
from django.http.response import HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceMeasure
from django.contrib.gis.db.models.functions import Distance as DistanceFunction, DistanceResultMixin
from django.db.models import Value, FloatField


from lib.geo import get_zipcode_centroid, FRENCH_ZIPCODE_REGEX


class SoftLoginRequiredMixin(object):
    unlogged_redirect_url = 'oauth_redirect_view'

    @staticmethod
    def get_message_string(user):
        return format_html(
            _("Bonjour {person} (ce n'est pas vous ? <a href=\"{login_url}\">Cliquez-ici pour vous reconnecter"
              "</a> avec votre compte.)"),
            person=user.person.get_short_name(),
            login_url=reverse('oauth_redirect_view')
        )

    def dispatch(self, request, *args, **kwargs):
        if 'p' in request.GET and 'code' in request.GET:
            # preserve other query params than p and code when we redirect
            other_params = request.GET.copy()
            del other_params['p']
            del other_params['code']
            url = '{}?{}'.format(request.path, other_params.urlencode(safe='/')) if other_params else request.path

            user = authenticate(user_pk=request.GET['p'], code=request.GET['code'])

            # case where user is already authenticated and different from user above ==> redirect with warning message
            if request.user.is_authenticated and request.user != user:
                messages.add_message(
                    request=request,
                    level=messages.WARNING,
                    message=self.get_message_string(request.user)
                )
                return HttpResponseRedirect(url)
            # case where user is being authenticated ==> we show a message but only with info level
            elif user:
                login(request, user)
                messages.add_message(
                    request=request,
                    level=messages.INFO,
                    message=self.get_message_string(user)
                )
                return HttpResponseRedirect(url)

        elif request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path(), self.unlogged_redirect_url)


class HardLoginRequiredMixin(object):
    unlogged_redirect_url = 'oauth_redirect_view'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.session[BACKEND_SESSION_KEY] != 'front.backend.MailLinkBackend':
            return super().dispatch(request, *args, **kwargs)

        return redirect_to_login(request.get_full_path(), self.unlogged_redirect_url)


class PermissionsRequiredMixin(object):
    permissions_required = ()
    permission_denied_message = _("Vous n'avez pas l'autorisation d'accéder à cette page.")

    def get_object(self):
        if not hasattr(self, '_cached_object'):
            self._cached_object = super().get_object()
        return self._cached_object

    def dispatch(self, *args, **kwargs):
        # check if there are some perms that the user does not have globally
        user = self.request.user
        local_perms = {perm for perm in self.permissions_required if not user.has_perm(perm)}

        if local_perms:
            obj = self.get_object()

            for perm in local_perms:
                if not user.has_perm(perm, obj):
                    raise PermissionDenied(self.permission_denied_message)

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
            meta_image=self.get_meta_image(),
            **kwargs
        )

    def get_meta_title(self):
        return self.meta_title

    def get_meta_description(self):
        return self.meta_description

    def get_meta_image(self):
        return None


class ObjectOpengraphMixin(SimpleOpengraphMixin):
    title_prefix = "La France insoumise"

    def get_meta_title(self):
        return '{} - {}'.format(self.title_prefix, self.object.name)

    def get_meta_image(self):
        if hasattr(self.object, 'image') and self.object.image:
            return urljoin(settings.FRONT_DOMAIN, self.object.image.url)
        return None


class ChangeLocationBaseView(UpdateView):
    # redefine in sub classes
    template_name = None
    form_class = None
    queryset = None
    success_view_name = None

    def get_success_url(self):
        return reverse(self.success_view_name, args=(self.object.pk,))

    def form_valid(self, form):
        res = super().form_valid(form)

        message = form.get_message()

        if message:
            messages.add_message(
                request=self.request,
                level=messages.SUCCESS,
                message=message
            )

        return res


class FixedDistance(DistanceResultMixin, Value):
    _output_field = FloatField()

    def __init__(self, **kwargs):
        distance = DistanceMeasure(**kwargs)
        super().__init__(distance.standard)

    def convert_value(self, value, expression, connection, context):
        if value is None:
            return None
        d = DistanceMeasure()
        d.standard = value
        return d


class SearchByZipcodeBaseView(ListView):
    """List of events, filter by zipcode
    """
    min_items = 20
    form_class = None
    queryset = None

    def get(self, request, *args, **kwargs):
        self.form = self.get_form()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=self.form,
            **kwargs,
        )

    def get_person_zipcode(self):
        if self.request.user.is_authenticated and self.request.user.person.location_zip and \
                FRENCH_ZIPCODE_REGEX.match(self.request.user.person.location_zip):
            return self.request.user.person.location_zip
        return None

    def get_form_kwargs(self):
        return {
            'data': self.request.GET or {'zipcode': self.get_person_zipcode()}
        }

    def get_form(self):
        return self.form_class(**self.get_form_kwargs())

    def get_base_queryset(self):
        return self.queryset

    def get_queryset(self):
        base_queryset = self.get_base_queryset()

        zipcode = self.get_zipcode()
        if not zipcode:
            return base_queryset.none()

        queryset = base_queryset.filter(location_zip=zipcode)\
            .annotate(distance=FixedDistance(m=0))

        if len(queryset) < self.min_items:
            centroid = get_zipcode_centroid(zipcode)
            if centroid:
                nearby = base_queryset.exclude(location_zip=zipcode) \
                             .annotate(distance=DistanceFunction('coordinates', Point(*centroid, srid=4326)))\
                             .order_by('distance')[:(self.min_items - len(queryset))]
                queryset = list(queryset) + list(nearby)

        return queryset

    def get_zipcode(self):
        if self.form.is_valid() and self.form.cleaned_data['zipcode']:
            return self.form.cleaned_data['zipcode']
        return None
