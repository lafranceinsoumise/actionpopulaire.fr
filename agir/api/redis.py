import redis
from django.conf import settings


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


def get_auth_redis_client():
    return redis.StrictRedis(connection_pool=auth_pool.pool)
