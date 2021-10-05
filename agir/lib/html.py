import re

import bleach
from django.conf import settings
from django.utils.html import mark_safe, strip_tags


def sanitize_html(text, tags=None):
    if tags is None:
        tags = settings.USER_ALLOWED_TAGS
    return mark_safe(bleach.clean(str(text), tags=tags, strip=True))


def textify(html):
    # Remove html tags and continuous whitespaces
    text_only = re.sub("[ \t]+", " ", strip_tags(html))
    # Strip single spaces in the beginning of each line
    return text_only.replace("\n ", "\n").strip()
