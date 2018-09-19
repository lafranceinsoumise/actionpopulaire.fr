import os

from django.utils import timezone
from redis.client import Script

from agir.api.redis import get_auth_redis_client as get_redis_client

__all__ = ['TokenBucket']


def get_current_timestamp():
    """Return current timestamp in second

    this function is used to make testing easier"""
    return timezone.now().timestamp()


class TokenBucket:
    def __init__(self, name, max, interval):
        """Instancies a Token bucket value

        :param name: a unique name for the token bucket, used to name the redis keys
        :param max: the maximum (and initial) value of the token bucket
        :param interval: the interval (in seconds) by which the bucket is refilled by one unit
        """
        self.name = name
        self.max = max
        self.interval = interval

    def has_tokens(self, id, amount=1):
        """Check if the specific `id` has at least `amount` tokens, and decrease the bucket if it is the case

        :param id: an id identifying the entity to test, must be convertible to a string
        :param amount: an integer or float value
        :return: whether the entity has the necessary tokens
        """

        key_prefix = f"TokenBucket:{self.name}:{str(id)}:"

        res = token_bucket_script(
            keys=[f"{key_prefix}v", f"{key_prefix}t"],
            args=[self.max, self.interval, get_current_timestamp(), amount],
            client=get_redis_client()
        )

        return bool(res)

    def reset(self, id):
        key_prefix = f"TokenBucket:{self.name}:{str(id)}:"
        get_redis_client().pipeline().delete(f"{key_prefix}v").delete(f"{key_prefix}t").execute()


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token_bucket.lua'), mode='rb') as f:
    token_bucket_script = Script(None, f.read())
