from typing import Mapping, Any

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


def escape_character(string, character):
    if not character:
        return string
    return string.replace("\\", "\\\\").replace(character, "\\" + character)


class SignatureGenerator(PasswordResetTokenGenerator):
    salt = None
    token_params = []
    params_separator = "|"
    ignored_params = ["android", "ios"]

    def __init__(self, days_validity, **kwargs):
        self.validity = days_validity * 24 * 60 * 60

        for key, value in kwargs.items():
            if not hasattr(self.__class__, key):
                raise TypeError(
                    "%s() a reçu un paramètre un argument invalide %r. Seuls les arguments qui sont déjà"
                    " des attributs de la classe sont acceptés."
                )

            setattr(self, key, value)

        super().__init__()

    def _check_params(self, params):
        return set(params).issuperset(set(self.token_params))

    def make_token(self, **params):
        if not self._check_params(params):
            raise TypeError(
                f"The following arguments are compulsory: {self.token_params!r}"
            )
        return self._make_token_with_timestamp(params, self._num_seconds(self._now()))

    def _make_hash_value(self, params: Mapping[str, Any], timestamp):
        # order the params by lexicographical order, so that there is some determinism
        sorted_keys = sorted(params)
        ordered_params = [
            params[k] for k in sorted_keys if k not in self.ignored_params
        ]

        return self.params_separator.join(
            escape_character(str(param), self.params_separator)
            for param in ordered_params
        ) + str(timestamp)

    def is_expired(self, token):
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        if ts < 7228:
            ts = ts * 24 * 60 * 60

        # Check the timestamp is within limit
        if (self._num_seconds(self._now()) - ts) > self.validity:
            return True

        return False

    def check_token(self, token, **params):
        """copied from"""
        if not self._check_params(params):
            return False
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
            self._make_token_with_timestamp(params, ts, legacy=ts < 7228), token
        ):
            return False

        if ts < 7228:
            ts = ts * 24 * 60 * 60

        # Check the timestamp is within limit
        if (self._num_seconds(self._now()) - ts) > self.validity:
            return False

        return True

    def get_timestamp(self, token):
        try:
            ts_b36, hash = token.split("-")
            return base36_to_int(ts_b36)
        except ValueError:
            return None


class ConnectionSignatureGenerator(SignatureGenerator):
    """Strategy object used to generate and check tokens used for connection links"""

    # not up to date, but changing it would invalidate all tokens
    key_salt = "front.backend.ConnectionTokenGenerator"
    token_params = ["user"]
    params_separator = ""

    def make_token(self, user):
        return super().make_token(user=user)

    def _make_hash_value(self, params, timestamp):
        # le hash n'est basé que sur l'ID de l'utilisateur et le timestamp

        user = params["user"]

        return str(user.pk) + str(user.auto_login_salt) + str(timestamp)
