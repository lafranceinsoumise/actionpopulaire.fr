import json
import re
from secrets import choice
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.utils.http import base36_to_int
from django.utils.crypto import constant_time_compare

from agir.api.redis import get_auth_redis_client


class ConnectionTokenGenerator(PasswordResetTokenGenerator):
    """Strategy object used to generate and check tokens used for connection"""
    key_salt = 'front.backend.ConnectionTokenGenerator'

    def __init__(self, validity):
        self.validity = validity

    def _make_hash_value(self, user, timestamp):
        # le hash n'est basé que sur l'ID de l'utilisateur et le timestamp
        return (
            str(user.pk) + str(timestamp)
        )

    def check_token(self, user, token):
        """
        Check that a connection token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) > self.validity:
            return False

        return True


class ShortCodeGenerator():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ123456789"
    allowed_patterns = [r'[A-Z1-9]{5}', r'[0-9]{8}']
    length = 5

    def __init__(self, key_prefix, validity, max_concurrent_codes):
        """

        :param key_prefix: redis prefix used to name the keys holding the tokens
        :param validity: duration of validity of generated tokens, in minutes
        :param max_concurrent_codes: maximum number of concurrent codes
        """
        self.key_prefix = key_prefix
        self.validity = validity
        self.max_concurrent_codes = max_concurrent_codes
        self._allowed_patterns = [re.compile(p) for p in self.allowed_patterns]

    def _make_code(self):
        return ''.join(choice(self.alphabet) for i in range(self.length))

    def generate_short_code(self, user_pk):
        short_code = self._make_code()
        expiration = timezone.now() + timezone.timedelta(minutes=self.validity)
        payload = json.dumps({
            'code': short_code,
            'expiration': int(expiration.timestamp()*1000)  # timestamp from epoch in microseconds
        })
        key = f"{self.key_prefix}{user_pk}"

        p = get_auth_redis_client().pipeline(transaction=False)
        p.lpush(key, payload)
        p.ltrim(key, 0, self.max_concurrent_codes - 1)
        p.expire(key, 60 * self.validity)
        p.execute()

        return short_code, expiration

    def is_allowed_pattern(self, code):
        return any(p.match(code) for p in self._allowed_patterns)

    def check_short_code(self, user_pk, short_code):
        key = f"{self.key_prefix}{user_pk}"
        now = timezone.now()

        # get the raw payloads for all codes
        raw_payloads = get_auth_redis_client().lrange(key, 0, self.max_concurrent_codes - 1)
        # parse the JSON payloads (but keep original payload to allow removing it from redis list)
        payloads = [json.loads(p) for p in raw_payloads]
        valid_short_codes = [p['code'] for p in payloads
                             if timezone.datetime.fromtimestamp(p['expiration'] / 1000, timezone.utc) > now]

        # to avoid timing attacks, always compare with every codes, and use constant time comparisons
        correct_short_code_payloads = [c for c in valid_short_codes
                               if constant_time_compare(c, short_code)]

        return bool(correct_short_code_payloads)
