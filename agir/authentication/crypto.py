import json
import re
from typing import Mapping, Any
from secrets import choice

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.utils.http import base36_to_int
from django.utils.crypto import constant_time_compare

from agir.api.redis import get_auth_redis_client


def escape_character(string, character):
    if not character:
        return string
    return string.replace("\\", "\\\\").replace(character, "\\" + character)


class BaseTokenGenerator(PasswordResetTokenGenerator):
    salt = None
    token_params = []
    params_separator = ""

    def __init__(self, validity):
        self.validity = validity

    def _check_params(self, params):
        if not set(params).issuperset(set(self.token_params)):
            raise TypeError(
                f"The following arguments are compulsory: {self.token_params!r}"
            )

    def make_token(self, **params):
        self._check_params(params)
        return self._make_token_with_timestamp(params, self._num_days(self._today()))

    def _make_hash_value(self, params: Mapping[str, Any], timestamp):
        # order the params by lexicographical order, so that there is some determinism
        sorted_keys = sorted(params)
        ordered_params = [params[k] for k in sorted_keys]

        return self.params_separator.join(
            escape_character(param, self.params_separator) for param in ordered_params
        ) + str(timestamp)

    def is_expired(self, token):
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) > self.validity:
            return True

        return False

    def check_token(self, token, **params):
        """copied from """
        self._check_params(params)
        if not token:
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
        if not constant_time_compare(
            self._make_token_with_timestamp(params, ts), token
        ):
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) > self.validity:
            return False

        return True


class ConnectionTokenGenerator(BaseTokenGenerator):
    """Strategy object used to generate and check tokens used for connection"""

    # not up to date, but changing it would invalidate all tokens
    key_salt = "front.backend.ConnectionTokenGenerator"
    token_params = ["user"]

    def make_token(self, user):
        return super().make_token(user=user)

    def _make_hash_value(self, params, timestamp):
        # le hash n'est basé que sur l'ID de l'utilisateur et le timestamp

        user = params["user"]

        return str(user.pk) + str(user.auto_login_salt) + str(timestamp)


class SubscriptionConfirmationTokenGenerator(BaseTokenGenerator):
    key_salt = "agir.people.crypto.SubscriptionConfirmationTokenGenerator"
    token_params = ["email"]
    params_separator = "|"


class AddEmailConfirmationTokenGenerator(BaseTokenGenerator):
    key_salt = "agir.people.crypto.AddEmailConfirmationTokenGenerator"
    token_params = ["user", "new_email"]
    params_separator = "|"


class ShortCodeGenerator:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ123456789"
    allowed_patterns = [r"[A-Z1-9]{5}", r"[0-9]{8}"]
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
        return "".join(choice(self.alphabet) for i in range(self.length))

    def generate_short_code(self, user_pk):
        short_code = self._make_code()
        expiration = timezone.now() + timezone.timedelta(minutes=self.validity)
        payload = json.dumps(
            {
                "code": short_code,
                "expiration": int(
                    expiration.timestamp() * 1000
                ),  # timestamp from epoch in microseconds
            }
        )
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
        raw_payloads = get_auth_redis_client().lrange(
            key, 0, self.max_concurrent_codes - 1
        )
        # parse the JSON payloads (but keep original payload to allow removing it from redis list)
        payloads = [json.loads(p) for p in raw_payloads]
        valid_short_codes = [
            p["code"]
            for p in payloads
            if timezone.datetime.fromtimestamp(p["expiration"] / 1000, timezone.utc)
            > now
        ]

        # to avoid timing attacks, always compare with every codes, and use constant time comparisons
        correct_short_code_payloads = [
            c for c in valid_short_codes if constant_time_compare(c, short_code)
        ]

        return bool(correct_short_code_payloads)


connection_token_generator = ConnectionTokenGenerator(settings.CONNECTION_LINK_VALIDITY)
short_code_generator = ShortCodeGenerator(
    "LoginCode:", settings.SHORT_CODE_VALIDITY, settings.MAX_CONCURRENT_SHORT_CODES
)
