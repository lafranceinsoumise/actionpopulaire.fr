import re
import secrets
from io import BytesIO
from itertools import chain, islice
from string import ascii_uppercase, digits
from urllib.parse import urljoin, urlparse, parse_qs

import pytz
import requests
from PIL import Image, ImageOps
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import QueryDict
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.utils.functional import lazy

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


def generate_token_params(person):
    return {"p": person.pk, "code": connection_token_generator.make_token(user=person)}


def resize_and_autorotate(file_name, variations, storage=default_storage):
    """
    Function to be used as value for StdImageField render_variations argument.
    Fix uploaded image file exif orientation after saving and before creating variations.
    """
    with storage.open(file_name) as f:
        with Image.open(f) as image:
            transposed_image = ImageOps.exif_transpose(image)
            if not getattr(storage, "file_overwrite", False):
                storage.delete(file_name)
            with BytesIO() as file_buffer:
                transposed_image.save(file_buffer, format=image.format)
                f = ContentFile(file_buffer.getvalue())
                storage.save(file_name, f)

    # Allow default render variations
    return True


def shorten_url(url, secret=False, djan_url_type="LFI"):
    djan_url = settings.DJAN_URL[djan_url_type]
    response = requests.post(
        f"{djan_url}/api/shorten",
        params={
            "token": settings.DJAN_API_KEY,
        },
        data={"url": url, "length": 10 if secret else 5},
        headers={"Authorization": f"Bearer {settings.DJAN_API_KEY}"},
    )
    response.raise_for_status()
    return response.text


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
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
        ),
    )


def validate_facebook_event_url(url):
    # Regular expression for FB event URLs with an event ID
    FACEBOOK_EVENT_ID_RE = re.compile(
        r"^(?:(?:https://)?(?:www\.)?(?:facebook|m\.facebook).com/events/)?([0-9]{15,20})(?:/.*)?$"
    )
    # Regular expression for FB regular and short event URLs
    FACEBOOK_EVENT_URL_RE = re.compile(
        r"^((?:https://)?(?:www\.)?(?:facebook|fb|m\.facebook)\.(?:com|me)/(?:events|e)/(?:\w{0,20}))(?:/.*)?$"
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


# Returns a clean email subject for new_message and new_comment < 80 chars
def clean_subject_email(subject):
    subject = subject.replace("\n", "")
    subject = re.sub("\s+", " ", subject)
    if len(subject) > 80:
        subject = subject[0:80] + '..."'
    return subject


def grouper(it, n):
    """Subdivise un itérateur en groupes successifs de taille maximale n"""
    if n <= 0:
        raise ValueError("`n` doit être en entier positif")
    it = iter(it)
    while True:
        try:
            f = next(it)
        except StopIteration:
            return
        yield chain((f,), islice(it, n - 1))


def get_youtube_video_id(url):
    """Returns Video_ID extracting from the given url of Youtube
    inspired by https://gist.github.com/kmonsoor/2a1afba4ee127cce50a0
    """
    if url.startswith(("youtu", "www")):
        url = "http://" + url

    query = urlparse(url)
    if query.hostname in ("www.youtube.com", "youtu.be", "youtube.com"):
        if parse_qs(query.query).get("v"):
            return parse_qs(query.query)["v"][0]

        if "youtube" in query.hostname and query.path.startswith(
            ("/embed/", "/e/", "/v/")
        ):
            return query.path.split("/")[2]

        if "youtu.be" in query.hostname:
            return query.path[1:]

    raise ValueError


ALPHABET = ascii_uppercase + digits
NUMERO_RE = re.compile("^[A-Z0-9]{3}-[A-Z0-9]{1,3}$")


def numero_unique():
    chars = [secrets.choice(ALPHABET) for _ in range(6)]
    return f"{''.join(chars[:3])}-{''.join(chars[3:])}"
