import re
from urllib.parse import urljoin

from django.conf import settings
from django.utils.http import urlquote


class TurbolinksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        location = urljoin(settings.FRONT_DOMAIN, urlquote(request.path))
        response["Turbolinks-Location"] = location

        return response


class NoVaryCookieMiddleWare:
    cc_delim_re = re.compile(r"\s*,\s*")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            not hasattr(response, "dont_vary_on_cookie")
            or not response.dont_vary_on_cookie
        ):
            return response

        if response.has_header("Vary"):
            vary_header = self.cc_delim_re.split(response["Vary"])
        else:
            # This response has no vary header, so don't change anything
            return response

        new_header = []
        for vary in vary_header:
            print(vary)
            if not vary.lower() == "cookie":
                new_header.append(vary)
        if len(new_header) > 0:
            response["Vary"] = ", ".join(new_header)
        else:
            del response["Vary"]

        return response
