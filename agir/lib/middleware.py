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
