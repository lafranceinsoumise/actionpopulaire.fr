import bleach
from django.conf import settings
from django.utils.html import mark_safe


def sanitize_html(text, tags=None):
    if tags is None:
        tags = settings.USER_ALLOWED_TAGS
    return mark_safe(bleach.clean(text, tags=tags, strip=True))
