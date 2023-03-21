import re
import textwrap
from urllib.parse import urljoin, urlunparse, urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.contrib.gis.db.models.functions import (
    Distance as DistanceFunction,
    DistanceResultMixin,
)
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceMeasure
from django.db.models import Value, FloatField
from django.http import QueryDict
from django.shortcuts import reverse, resolve_url
from django.templatetags.static import static
from django.views.generic import UpdateView, ListView
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin


class SimpleOpengraphMixin(ContextMixin):
    meta_title = None
    meta_description = None
    meta_type = "article"
    meta_image = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            show_opengraph=True,
            meta_title=self.get_meta_title(),
            meta_description=self.get_meta_description(),
            meta_type=self.meta_type,
            meta_image=self.get_meta_image(),
            **kwargs,
        )

    def get_meta_title(self):
        return self.meta_title

    def get_meta_description(self, max_width=None):
        return self.meta_description

    def get_meta_image(self):
        return self.meta_image

    def redirect_to_login(self, request, *args, **kwargs):
        description = self.get_meta_description()
        if isinstance(description, str) and len(description) > 255:
            description = re.split("(?<=[.!?])[\n\r\s]+", description)[0]
            description = textwrap.shorten(description, width=255, placeholder="…")

        meta_tags = {
            "title": self.get_meta_title(),
            "description": description,
            "image": self.get_meta_image(),
        }

        login_url = resolve_url(settings.LOGIN_URL)

        login_url_parts = list(urlparse(login_url))
        for key, value in meta_tags.items():
            if not value:
                continue
            querystring = QueryDict(login_url_parts[4], mutable=True)
            querystring[f"meta_{key}"] = value
            login_url_parts[4] = querystring.urlencode(safe="/")

        return redirect_to_login(
            request.get_full_path(), login_url=urlunparse(login_url_parts)
        )


class ObjectOpengraphMixin(SimpleOpengraphMixin):
    title_suffix = "Action Populaire"

    # noinspection PyUnresolvedReferences
    def get_meta_title(self):
        return "{} — {}".format(self.object.name, self.title_suffix)

    # noinspection PyUnresolvedReferences
    def get_meta_image(self):
        url = static("front/assets/og_image_NSP.jpg")
        if hasattr(self.object, "image") and self.object.image:
            url = self.object.image.url
        return urljoin(settings.FRONT_DOMAIN, url)


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
                request=self.request, level=messages.SUCCESS, message=message
            )

        return res


class FixedDistance(DistanceResultMixin, Value):
    _output_field = FloatField()

    def __init__(self, **kwargs):
        distance = DistanceMeasure(**kwargs)
        super().__init__(distance.standard)

    # noinspection PyMethodOverriding
    def convert_value(self, value, expression, connection, context):
        if value is None:
            return None
        d = DistanceMeasure()
        d.standard = value
        return d


class SearchByZipcodeBaseView(ListView):
    """List of events, filter by zipcode"""

    paginate_by = 20
    form_class = None
    queryset = None

    def get(self, request, *args, **kwargs):
        self.form = self.get_form()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(form=self.form, **kwargs)

    def get_person_location(self):
        if self.request.user.is_authenticated:
            return self.request.user.person.coordinates
        return None

    def get_form_kwargs(self):
        person_location = self.get_person_location()

        lon, lat = self.request.GET.get("lon", None), self.request.GET.get("lat", None)

        if (not lat or not lon) and person_location:
            lon, lat = person_location

        return {"data": {"lon": lon, "lat": lat, "q": self.request.GET.get("q", "")}}

    def get_form(self):
        return self.form_class(**self.get_form_kwargs())

    def get_base_queryset(self):
        return self.queryset

    def get_queryset(self):
        base_queryset = self.get_base_queryset()

        location = self.get_location()
        if not location:
            return base_queryset.none()

        queryset = base_queryset.annotate(
            distance=DistanceFunction("coordinates", location)
        ).order_by("distance")

        return queryset

    def get_location(self):
        if self.form.is_valid():
            lon, lat = self.form.cleaned_data["lon"], self.form.cleaned_data["lat"]
            if lat and lon:
                return Point(lon, lat, srid=4326)
        return None


class FilterView(FormMixin, ListView):
    filter_class = None
    queryset = None

    def get_filter(self):
        return self.filter_class(data=self.request.GET, queryset=self.queryset)

    def get_queryset(self):
        return self.get_filter().qs

    def get_form(self, form_class=None):
        return self.get_filter().form


class ReactBaseView(TemplateView):
    bundle_name = "front/app"
    app_mount_id = "mainApp"
    template_name = "front/react_view.html"
    api_preloads = []
    page_schema = None

    def get_api_preloads(self):
        return self.api_preloads

    def get_page_schema(self):
        return self.page_schema

    def get_context_data(self, **kwargs):
        kwargs.setdefault("bundle_name", self.bundle_name)
        kwargs.setdefault("app_mount_id", self.app_mount_id)
        kwargs.setdefault("api_preloads", self.get_api_preloads())
        kwargs.setdefault("page_schema", self.get_page_schema())
        return super().get_context_data(**kwargs)


class ReactSerializerBaseView(ReactBaseView):
    serializer_class = None
    data_script_id = "exportedContent"

    def get_serializer(self):
        raise NotImplementedError("Should be implemented in concrete classes")

    def get_export_data(self):
        return self.get_serializer().data

    def get_context_data(self, **kwargs):
        kwargs.setdefault("export_data", self.get_export_data())
        kwargs.setdefault("data_script_id", self.data_script_id)
        return super().get_context_data(**kwargs)


class ReactSingleObjectView(SingleObjectMixin, ReactSerializerBaseView):
    template_name = "front/react_view.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_serializer(self):
        return self.serializer_class(
            instance=self.object, context={"request": self.request}
        )
