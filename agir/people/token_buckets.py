from agir.lib.token_bucket import TokenBucket


ChangeMailBucket = TokenBucket("ConfirmationChangeMail", 5, 180)
"""Bucket used to limit subscription by email

Burst of 10, then 1 every 3 minutes
"""
