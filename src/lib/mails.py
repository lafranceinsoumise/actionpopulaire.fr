from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.core.mail import EmailMultiAlternatives

import html2text

import requests

__all__ = ['get_mosaico_email', 'send_mail']


def get_mosaico_email(code, recipient, **kwargs):
    if code not in settings.EMAIL_TEMPLATES:
        raise ImproperlyConfigured("Mail '%s' cannot be found")

    url = settings.EMAIL_TEMPLATES[code]

    qs = QueryDict(mutable=True)
    qs.update(kwargs)
    qs['EMAIL'] = recipient

    # We first initialize the LINK_BROWSER variable as "#" (same page)
    qs['LINK_BROWSER'] = "#"
    # we generate the final browser link and add it to the query string
    qs['LINK_BROWSER'] = f"{url}?{qs.urlencode()}"

    # requests the full url (including the final browser link)
    response = requests.get(f"{url}?{qs.urlencode()}")
    response.raise_for_status()

    return response.text


def send_mail(subject, html_message, from_email, recipient_list, fail_silently=False, connection=None):
    h = html2text.HTML2Text()
    h.ignore_images = True

    text_message = h.handle(html_message)

    msg = EmailMultiAlternatives(subject, text_message, from_email, recipient_list, connection=connection)
    msg.attach_alternative(html_message, "text/html")
    msg.send(fail_silently=fail_silently)
