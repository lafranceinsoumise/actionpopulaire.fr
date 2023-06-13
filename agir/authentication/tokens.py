import json
from secrets import choice

import re

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from agir.api.redis import get_auth_redis_client
from agir.authentication.crypto import ConnectionSignatureGenerator
from .crypto import SignatureGenerator

subscription_confirmation_token_generator = SignatureGenerator(
    7,
    key_salt="agir.people.crypto.SubscriptionConfirmationTokenGenerator",
    token_params=["email"],
    params_separator="|",
)  # Token generator for subscription confirmation links, used for double optin

add_email_confirmation_token_generator = SignatureGenerator(
    7,
    key_salt="agir.people.crypto.AddEmailConfirmationTokenGenerator",
    token_params=["user", "new_email"],
    params_separator="|",
)  # Token generator to add an email to an existing account

merge_account_token_generator = SignatureGenerator(
    7,
    key_salt="agir.people.crypto.MergeAccountTokenGenerator",
    token_params=["pk_requester", "pk_merge"],
    params_separator="|",
)  # Token generator to merge two accounts

invitation_confirmation_token_generator = SignatureGenerator(
    7,
    key_salt="agir.people.crypto.InvitationConfirmationTokenGenerator",
    token_params=["person_id", "group_id"],
    params_separator="|",
)  # Token generator for invitation sent to join a group

abusive_invitation_report_token_generator = SignatureGenerator(
    7,
    key_salt="agir.people.crypto.AbusiveInvitationReportingSignatureGenerator",
    token_params=["group_id", "inviter_id"],
    params_separator="|",
)  # Token generator to report an abusive invitation

monthly_donation_confirmation_token_generator = SignatureGenerator(
    2,
    key_salt="monthly_donation_confirmation_token_generator",
    token_params=["email", "amount"],
    params_separator="|",
)  # Token generator to confirm monthly donation when user not logged in

connection_token_generator = ConnectionSignatureGenerator(
    settings.CONNECTION_LINK_VALIDITY
)


class ShortCodeGenerator:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ123456789"
    allowed_patterns = [r"^[A-Z1-9]{5}$"]
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

    def generate_short_code(self, user_pk, meta: dict = None):
        if meta is None:
            meta = {}

        short_code = self._make_code()
        expiration = timezone.now() + timezone.timedelta(minutes=self.validity)
        payload = json.dumps(
            {
                "code": short_code,
                "expiration": int(
                    expiration.timestamp() * 1000
                ),  # timestamp from epoch in microseconds
                "meta": meta,
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
            p
            for p in payloads
            if timezone.datetime.fromtimestamp(p["expiration"] / 1000, timezone.utc)
            > now
        ]

        # to avoid timing attacks, always compare with every codes, and use constant time comparisons
        correct_short_code_payloads = [
            p for p in valid_short_codes if constant_time_compare(p["code"], short_code)
        ]

        if correct_short_code_payloads:
            meta = correct_short_code_payloads[0].get("meta", {})
            meta.setdefault(
                "_valid", True
            )  # comme ça la valeur booléenne du dict est vraie pour pouvoir faire `if gen.check_short_code(pk, tok):`
            return meta

        return None


short_code_generator = ShortCodeGenerator(
    "LoginCode:", settings.SHORT_CODE_VALIDITY, settings.MAX_CONCURRENT_SHORT_CODES
)
