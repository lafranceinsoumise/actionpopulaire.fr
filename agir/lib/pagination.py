from collections import OrderedDict

from django.core.paginator import Paginator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CachedCountPaginator(Paginator):
    @cached_property
    def count(self):
        # only select 'id' for counting, much cheaper
        return self.object_list.values("pk").count()


class APIPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    django_paginator_class = CachedCountPaginator


class LegacyPaginator(PageNumberPagination):
    """
    A legacy paginator that mocks the one from Eve Python
    """

    page_size = 25
    page_size_query_param = "max_results"
    max_page_size = 100

    def get_paginated_response(self, data):
        links = OrderedDict()
        if self.page.has_next():
            links["next"] = OrderedDict(
                [("href", self.get_next_link()), ("title", _("page suivante"))]
            )
        if self.page.has_previous():
            links["prev"] = OrderedDict(
                [("href", self.get_previous_link()), ("title", _("page précédente"))]
            )

        meta = OrderedDict(
            [
                ("max_results", self.page.paginator.per_page),
                ("total", self.page.paginator.count),
                ("page", self.page.number),
            ]
        )

        return Response(
            OrderedDict([("_items", data), ("_links", links), ("_meta", meta)])
        )
