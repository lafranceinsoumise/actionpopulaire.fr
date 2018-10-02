import base64
from functools import wraps
from hashlib import sha1

from django.http import HttpResponse
from django.utils.crypto import constant_time_compare


EMPTY_HASH = sha1().digest()


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

    def __init__(self, content=b'', realm="api", *args, **kwargs):
        super().__init__(content, *args, **kwargs)
        self['WWW-Authenticate'] = f'Basic realm="{realm}"'


def check_basic_auth(request, identities):
    auth = request.META.get('HTTP_AUTHORIZATION', '').split()

    if len(auth) != 2 or auth[0].lower() != 'basic':
        return HttpResponseUnauthorized()

    try:
        user, password = base64.b64decode(auth[1]).decode().split(':')
    except:
        return HttpResponseUnauthorized()

    h = sha1()
    h.update(password)
    digest = h.digest()

    user_exists = user in identities
    identical_password = constant_time_compare(digest, identities.get(user, EMPTY_HASH))

    if not user_exists or not identical_password:
        return HttpResponseUnauthorized()


def with_http_basic_auth(identities):
    hashed_identities = {}
    for user, password in identities.items():
        h = sha1()
        h.update(password.encode('utf8'))
        hashed_identities[user] = h.digest()

    def decorator(view):
        if isinstance(view, type):
            wrapped_dispatch = type.dispatch
            @wraps(wrapped_dispatch)
            def wrapper(self, request, *args, **kwargs):
                check_basic_auth(request, hashed_identities)
                return wrapped_dispatch(self, request, *args, **kwargs)
            view.dispatch = wrapper
            return view

        @wraps(view)
        def wrapper(request, *args, **kwargs):
            check_basic_auth(request, hashed_identities)
            return view(request, *args, **kwargs)
        return wrapper

    return decorator
