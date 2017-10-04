from urllib.parse import urljoin

from django.shortcuts import reverse
from django.conf import settings
from django.http import QueryDict

from .backend import token_generator


def _querydict_from_dict(d):
    q = QueryDict(mutable=True)
    q.update(d)
    return q


def front_url(*args, query=None, **kwargs):
    url = urljoin(settings.FRONT_DOMAIN, reverse(*args, urlconf='front.urls', **kwargs))
    if query:
        if isinstance(query, dict):
            url = "{}?{}".format(url, _querydict_from_dict(query).urlencode(safe='/'))
        else:
            url = ["{}?{}".format(url, _querydict_from_dict(q).urlencode(safe='/')) for q in query]
    return url


def generate_token_params(person):
    return {
        'p': person.pk,
        'code': token_generator.make_token(person)
    }
