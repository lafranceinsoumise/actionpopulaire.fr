from collections import OrderedDict
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

from django.core.paginator import Paginator, Page
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class HTMLPage(Page):
    def __init__(self, *args, base_url, **kwargs):
        self.base_url = base_url
        super().__init__(*args, **kwargs)

    def pagination_nav(self):
        start, end = (
            max(2, self.number - 4),
            min(self.paginator.num_pages - 1, self.number + 4),
        )

        if start == 2:
            start = 1
            show_first_page = False
        else:
            show_first_page = True

        if end == self.paginator.num_pages - 1:
            end = self.paginator.num_pages
            show_last_page = False
        else:
            show_last_page = True

        template = get_template("lib/pagination.html")
        return template.render(
            {
                "page_obj": self,
                "page_range": range(start, end + 1),
                "base_url": self.base_url,
                "show_first_page": show_first_page,
                "show_last_page": show_last_page,
            }
        )


class HTMLPaginator(Paginator):
    def __init__(self, *args, request, **kwargs):
        url = urlparse(request.get_full_path())
        query = parse_qs(url.query)
        query.pop("page", None)
        base_url = urlunparse(url._replace(query=urlencode(query, True)))
        if query:
            base_url += "&"
        else:
            base_url += "?"

        self.base_url = base_url
        super().__init__(*args, **kwargs)

    def _get_page(self, *args, **kwargs):
        return HTMLPage(*args, base_url=self.base_url, **kwargs)


class APIPaginator(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


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
