from django.utils.translation import ugettext_lazy as _
from agir.lib.token_bucket import TokenBucket


SubscribeIPBucket = TokenBucket("SubscribeIP", 4, 600)
"""Bucket used to limit subscription by IP

Burst of 4, then 1 every 10 minutes (more than enough for one person,
but we have to keep in mind that IPs can be shared between multiple
persons.
"""


SubscribeEmailBucket = TokenBucket("SubscribeEmail", 3, 1800)
"""Bucket used to limit subscription by email

Burst of 3, then 1 every half an hour (should be more than enough,
as emails should only be subscribed once in theory)
"""


subscription_rate_limited_message = _(
    "Vous avez fait trop de tentatives d'inscription. Consultez vos mails, pour vérifier que vous n'avez pas reçu le"
    " message de confirmation, ou patientez un peu avant de retenter."
)


def is_rate_limited_for_subscription(*, ip, email):
    return not SubscribeIPBucket.has_tokens(ip) or not SubscribeEmailBucket.has_tokens(
        email
    )
