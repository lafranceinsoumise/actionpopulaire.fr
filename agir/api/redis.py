from functools import wraps

import redis
from django.conf import settings
from unittest.mock import patch


class RedisPool:
    def __init__(self, url, max_connections):
        self._url = url
        self._max_connections = max_connections
        self._pool = None

    @property
    def pool(self):
        if self._pool is None:
            self._pool = redis.ConnectionPool.from_url(
                url=self._url,
                max_connections=self._max_connections
            )

        return self._pool


auth_pool = RedisPool(settings.AUTH_REDIS_URL, settings.AUTH_REDIS_MAX_CONNECTIONS)


def _get_auth_redis_client():
    return redis.StrictRedis(connection_pool=auth_pool.pool)


def get_auth_redis_client():
    return _get_auth_redis_client()


class _UsingRedisLite():
    def __call__(self, decorated=None):
        if decorated is None:
            return self.get_patcher()
        if isinstance(decorated, type):
            return self.decorate_class(decorated)
        return self.decorate_callable(decorated)

    def decorate_class(self, klass):
        for attr in dir(klass):
            if not attr.startswith(patch.TEST_PREFIX):
                continue

            attr_value = getattr(klass, attr)
            if not hasattr(attr_value, "__call__"):
                continue

            setattr(klass, attr, self(attr_value))
        return klass

    def decorate_callable(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.get_patcher():
                func(*args, **kwargs)

        return wrapper

    def get_patcher(self):
        import redislite
        connection = redislite.StrictRedis()
        return patch('agir.api.redis._get_auth_redis_client', lambda: connection)


using_redislite = _UsingRedisLite()
