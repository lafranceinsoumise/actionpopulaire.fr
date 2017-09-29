from urllib.parse import urljoin
from django.shortcuts import reverse
from django.conf import settings


def front_url(*args, **kwargs):
    return urljoin(settings.FRONT_DOMAIN, reverse(*args, urlconf='front.urls', **kwargs))
