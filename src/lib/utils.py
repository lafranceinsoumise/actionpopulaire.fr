from urllib.parse import urljoin

import six
from django.conf import settings
from django.http import QueryDict
from django.urls import reverse
from django.utils.functional import lazy

from front.backend import token_generator


def _querydict_from_dict(d):
    q = QueryDict(mutable=True)
    q.update(d)
    return q


def front_url(*args, query=None, absolute=True, **kwargs):
    url = reverse(*args, urlconf='api.front_urls', **kwargs)
    if absolute:
        url = urljoin(settings.FRONT_DOMAIN, url)
    if query:
        url = "{}?{}".format(url, _querydict_from_dict(query).urlencode(safe='/'))
    return url


front_url_lazy = lazy(front_url, six.text_type)


def is_front_url(param):
    return param.startswith(settings.FRONT_DOMAIN)


def generate_token_params(person):
    return {
        'p': person.pk,
        'code': token_generator.make_token(person)
    }
