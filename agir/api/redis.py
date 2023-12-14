from contextlib import contextmanager
from unittest.mock import patch

import redis
from django.conf import settings
from functools import wraps


class RedisPool:
    def __init__(self, url, max_connections):
        self._url = url
        self._max_connections = max_connections
        self._pool = None

    @property
    def pool(self):
        if self._pool is None:
            self._pool = redis.ConnectionPool.from_url(
                url=self._url, max_connections=self._max_connections
            )

        return self._pool


auth_pool = RedisPool(settings.REDIS_AUTH_URL, settings.REDIS_AUTH_MAX_CONNECTIONS)


# utilisé pour patcher facilement Redis en mode test
_test_redis_client = None


def get_auth_redis_client():
    if _test_redis_client is not None:
        return _test_redis_client
    return redis.StrictRedis(connection_pool=auth_pool.pool)


@contextmanager
def _patch_up_redislite():
    import redislite

    global _test_redis_client
    previous_redis_instance = _test_redis_client
    _test_redis_client = redislite.StrictRedis()

    try:
        yield _test_redis_client
    finally:
        _test_redis_client.close()
        _test_redis_client = previous_redis_instance


def using_separate_redis_server(decorated=None):
    """Start up a new redis server and gives back a connection to that server

    `using_separate_redis_server` can be used either as a context manager, a function decorator, or a child class of
    `TestCase`, in which case it will automatically decorate all the `test_` methods.

    :param decorated: the function or class to decorate, when it is used as a decorator
    :return:
    """
    if decorated is None:
        return _patch_up_redislite()
    if isinstance(decorated, type):
        for attr in dir(decorated):
            if not attr.startswith(patch.TEST_PREFIX):
                continue

            attr_value = getattr(decorated, attr)
            if not hasattr(attr_value, "__call__"):
                continue

            setattr(decorated, attr, using_separate_redis_server(attr_value))
        return decorated

    @wraps(decorated)
    def inner(*args, **kwargs):
        with _patch_up_redislite():
            return decorated(*args, **kwargs)

    return inner
