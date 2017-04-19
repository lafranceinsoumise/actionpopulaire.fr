import redis
from django.conf import settings


_pool = redis.ConnectionPool.from_url(
    url=settings.AUTH_REDIS_URL,
    max_connections=settings.AUTH_REDIS_MAX_CONNECTIONS
)


def get_redis_client():
    return redis.StrictRedis(connection_pool=_pool)
