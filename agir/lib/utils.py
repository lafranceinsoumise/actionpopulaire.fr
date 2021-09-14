from urllib.parse import urljoin, urlparse

import re
import pytz
import requests
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import QueryDict
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.utils.functional import lazy
from io import BytesIO
from stdimage.utils import render_variations

from agir.authentication.tokens import connection_token_generator
from agir.lib.http import add_query_params_to_url

INVALID_FACEBOOK_EVENT_LINK_MESSAGE = (
    "Vous devez indiquez soit l'identifiant de la page Facebook, soit son URL"
)


def _querydict_from_dict(d):
    q = QueryDict(mutable=True)
    q.update(d)
    return q


class AutoLoginUrl(str):
    def __str__(self):
        return self


def front_url(
    *args,
    query=None,
    absolute=True,
    auto_login=True,
    nsp=False,
    urlconf="agir.api.front_urls",
    **kwargs,
):
    url = reverse(*args, urlconf=urlconf, **kwargs)
    if absolute and not nsp:
        url = urljoin(settings.FRONT_DOMAIN, url)
    if absolute and nsp:
        url = urljoin(settings.NSP_AGIR_DOMAIN, url)
    if query:
        url = add_query_params_to_url(url, query)
    return AutoLoginUrl(url) if auto_login else url


front_url_lazy = lazy(front_url, str)


def admin_url(viewname, args=None, kwargs=None, query=None, absolute=True):
    if not viewname.startswith("admin:"):
        viewname = f"admin:{viewname}"

    url = reverse(viewname, args=args, kwargs=kwargs, urlconf="agir.api.admin_urls")
    if absolute:
        url = urljoin(settings.API_DOMAIN, url)
    if query:
        url = add_query_params_to_url(url, query)
    return url


def is_front_url(param):
    return isinstance(param, str) and param.startswith(settings.FRONT_DOMAIN)


def generate_token_params(person):
    return {"p": person.pk, "code": connection_token_generator.make_token(user=person)}


def resize_and_autorotate(
    file_name, variations, replace=False, storage=default_storage
):
    with storage.open(file_name) as f:
        with Image.open(f) as image:
            file_format = image.format
            try:
                exif = image._getexif()
            except AttributeError:
                exif = None

            # if image has exif data about orientation, let's rotate it
            orientation_key = 274  # cf ExifTags
            if exif and orientation_key in exif:
                orientation = exif[orientation_key]

                rotate_values = {
                    3: Image.ROTATE_180,
                    6: Image.ROTATE_270,
                    8: Image.ROTATE_90,
                }

                if orientation in rotate_values:
                    image = image.transpose(rotate_values[orientation])

            with BytesIO() as file_buffer:
                image.save(file_buffer, file_format)
                f = ContentFile(file_buffer.getvalue())
                storage.delete(file_name)
                storage.save(file_name, f)

    # render stdimage variations
    render_variations(file_name, variations, replace=replace, storage=storage)

    return False


def shorten_url(url, secret=False):
    return requests.post(
        settings.DJAN_URL + "/api/shorten",
        params={"token": settings.DJAN_API_KEY,},
        data={"url": url, "length": 10 if secret else 5},
    ).text


def get_client_ip(request):
    if settings.TRUST_X_FORWARDED_FOR:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

    return request.META["REMOTE_ADDR"]


def is_absolute_url(url):
    return isinstance(url, str) and url != "" and bool(urlparse(url).netloc)


def replace_datetime_timezone(dt, timezone_name):
    timezone = pytz.timezone(timezone_name)
    return timezone.localize(
        datetime(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond,
        ),
    )


def validate_facebook_event_url(url):
    # Regular expression for FB event URLs with an event ID
    FACEBOOK_EVENT_ID_RE = re.compile(
        r"^(?:(?:https://)?(?:www\.)?(?:facebook|m\.facebook).com/events/)?([0-9]{15,20})(?:/.*)?$"
    )
    # Regular expression for FB regular and short event URLs
    FACEBOOK_EVENT_URL_RE = re.compile(
        r"^((?:https://)?(?:www\.)?(?:facebook|fb|m\.facebook)\.(?:com|me)/(?:events|e)/(?:\d\w{0,20}))(?:/.*)?$"
    )

    # First we try to match an URL with an FB event ID (for backward compatibility)
    match = FACEBOOK_EVENT_ID_RE.match(url)
    if match:
        return f"https://www.facebook.com/events/{match.group(1)}"
    # If no FB id is found, we try to match a supported FB event URL (e.g. to allow for short URLs)
    match = FACEBOOK_EVENT_URL_RE.match(url)
    if match:
        return match.group(1)

    return False


def clean_subject_email(subject):
    subject = subject.replace("\n", "")
    subject = re.sub("\s+", " ", subject)
    if len(subject) > 80:
        subject = subject[0:80] + '..."'
    return subject
