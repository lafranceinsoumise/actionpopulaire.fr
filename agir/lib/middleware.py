from urllib.parse import urljoin

from django.conf import settings


class TurbolinksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response["Turbolinks-Location"] = urljoin(settings.FRONT_DOMAIN, request.path)

        return response
