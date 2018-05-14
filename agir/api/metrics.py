import base64
from django.conf import settings
from django.http import HttpResponse
from prometheus_client import multiprocess, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

    def __init__(self, content=b'', *args, **kwargs):
        super().__init__(content, *args, **kwargs)
        self['WWW-Authenticate'] = 'Basic realm="prometheus"'


def get_metrics(request):
    auth = request.META.get('HTTP_AUTHORIZATION', '').split()

    if len(auth) != 2 or auth[0].lower() != 'basic':
        return HttpResponseUnauthorized()

    try:
        user, password = base64.b64decode(auth[1]).decode().split(':')
    except:
        return HttpResponseUnauthorized()

    if user != settings.PROMETHEUS_USER or password != settings.PROMETHEUS_PASSWORD:
        return HttpResponseUnauthorized()

    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
