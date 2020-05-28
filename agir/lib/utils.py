from urllib.parse import urljoin

import requests
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import QueryDict
from django.urls import reverse
from django.utils.functional import lazy
from io import BytesIO
from stdimage.utils import render_variations

from agir.authentication.tokens import connection_token_generator
from agir.lib.http import add_query_params_to_url


def _querydict_from_dict(d):
    q = QueryDict(mutable=True)
    q.update(d)
    return q


class AutoLoginUrl(str):
    def __str__(self):
        return self


def front_url(*args, query=None, absolute=True, auto_login=True, **kwargs):
    url = reverse(*args, urlconf="agir.api.front_urls", **kwargs)
    if absolute:
        url = urljoin(settings.FRONT_DOMAIN, url)
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
    return requests.get(
        settings.POLR_URL + "/api/v2/action/shorten",
        params={
            "key": settings.POLR_API_KEY,
            "url": url,
            "is_secret": "true" if secret else "false",
        },
    ).text
