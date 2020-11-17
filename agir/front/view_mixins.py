from urllib.parse import urljoin

from django.conf import settings
from django.contrib import messages
from django.contrib.gis.db.models.functions import (
    Distance as DistanceFunction,
    DistanceResultMixin,
)
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceMeasure
from django.core.paginator import Paginator
from django.db.models import Value, FloatField
from django.shortcuts import reverse
from django.views.generic import UpdateView, ListView
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin


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

    def get_meta_description(self):
        return self.meta_description

    def get_meta_image(self):
        return self.meta_image


class ObjectOpengraphMixin(SimpleOpengraphMixin):
    title_prefix = "La France insoumise"

    # noinspection PyUnresolvedReferences
    def get_meta_title(self):
        return "{} - {}".format(self.title_prefix, self.object.name)

    # noinspection PyUnresolvedReferences
    def get_meta_image(self):
        if hasattr(self.object, "image") and self.object.image:
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
    """List of events, filter by zipcode
    """

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
    bundle_name = None
    data_script_id = "exportedContent"
    app_mount_id = "mainApp"
    template_name = "front/react_view.html"

    def get_context_data(self, **kwargs):
        kwargs.setdefault("bundle_name", self.bundle_name)
        kwargs.setdefault("app_mount_id", self.app_mount_id)
        kwargs.setdefault("data_script_id", self.data_script_id)
        return super().get_context_data(**kwargs)


class ReactSerializerBaseView(ReactBaseView):
    serializer_class = None

    def get_serializer(self):
        raise NotImplementedError("Should be implemented in concrete classes")

    def get_export_data(self):
        return self.get_serializer().data

    def get_context_data(self, **kwargs):
        kwargs.setdefault("export_data", self.get_export_data())
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


class ReactListView(MultipleObjectMixin, ReactSerializerBaseView):
    bundle_name = None
    serializer_class = None

    data_script_id = "exportedContent"
    app_mount_id = "mainApp"

    template_name = "front/react_view.html"

    page_size = None
    paginator_class = Paginator
    ordering = None

    def get_serializer(self):
        return self.serializer_class(
            instance=self.queryset, context={"request": self.request}, many=True
        )

    def get(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()
        self.is_paginated = False
        page_size = self.get_paginate_by(self.queryset)
        if page_size:
            (
                self.paginator,
                self.page,
                self.queryset,
                self.is_paginated,
            ) = self.paginate_queryset(self.queryset, page_size)

        return super().get(request, *args, **kwargs)

    def get_export_data(self):
        export = {"data": self.get_serializer().data, "links": {}}

        if self.is_paginated:
            if self.page.has_previous():
                export["links"]["previous"] = self.page.previous_page_number()
            if self.page.has_next():
                export["links"]["next"] = self.page.next_page_number()
            export["links"]["last"] = self.paginator.num_pages

        return export

    def get_context_data(self, **kwargs):
        # le get_context_data de MultipleObjectMixin recalculerait la pagination,
        # on préfère donc le skipper
        return super(MultipleObjectMixin, self).get_context_data(**kwargs)
