from collections import Sequence

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.core.mail import EmailMultiAlternatives, get_connection

import html2text

import requests

__all__ = ['fetch_mosaico_message', 'send_mail', 'send_mosaico_email']

_h = html2text.HTML2Text()
_h.ignore_images = True


def _iterate_recipients_bindings(recipients, bindings):
    """Iterates over recipients and bindings, some of them can be list of the same length as recipients
    :return:
    """
    multiple_bindings = [k for k, v in bindings.items() if isinstance(v, list) or isinstance(v, tuple)]
    l = len(recipients)

    assert all(len(bindings[b]) == l for b in multiple_bindings), "All bindings should be the same size as the recipient list"

    for recipient, *values in zip(recipients, *(bindings[k] for k in multiple_bindings)):
        yield (recipient, {**bindings, **dict(zip(multiple_bindings, values))})


def generate_plain_text(html_message):
    return _h.handle(html_message)


def fetch_mosaico_message(code, recipient, bindings):
    """Fetch the basic Mosaico template

    All replacements are done by the Mosaico server

    A possible optimization would be to instead fetch the message
    without replacing, and then replacing locally: it would help
    when sending the same message to many recipients by allowing only
    one GET request, vs. making one GET request per recipient
    """
    if code not in settings.EMAIL_TEMPLATES:
        raise ImproperlyConfigured("Mail '%s' cannot be found")

    url = settings.EMAIL_TEMPLATES[code]

    qs = QueryDict(mutable=True)
    qs.update(bindings)
    qs['EMAIL'] = recipient

    # We first initialize the LINK_BROWSER variable as "#" (same page)
    qs['LINK_BROWSER'] = "#"
    # we generate the final browser link and add it to the query string
    qs['LINK_BROWSER'] = f"{url}?{qs.urlencode()}"

    # requests the full url (including the final browser link)
    response = requests.get(f"{url}?{qs.urlencode()}")
    response.raise_for_status()

    return response.text


def send_mosaico_email(code, subject, from_email, recipients, bindings=None, connection_links=None, connection=None, backend=None,
                       fail_silently=False):
    """Send an email from a Mosaico template

    :param code: the code identifying the Mosaico template
    :param subject: the subject line of the email
    :param from_email: the address from which the email is to be sent
    :param recipients: a list of recipients to which the email will be send; alternatively, a single address
    :param bindings: a dictionary of replacements variables and their target values in the Mosaico template
    :param connection: an optional email server connection to use to send the emails
    :param backend: if no connection is given, an optional mail backend to use to send the emails
    :param fail_silently: whether any error should be raised, or just be ignored; by default it will raise
    """
    if isinstance(recipients, str):
        recipients = [recipients]

    if bindings is None:
        bindings = {}

    if connection is None:
        connection = get_connection(backend, fail_silently)

    for recipient, binding in _iterate_recipients_bindings(recipients, bindings):

        html_message = fetch_mosaico_message(code, recipient, binding)
        text_message = generate_plain_text(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=from_email,
            to=[recipient],
            connection=connection
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=fail_silently)


def send_mail(subject, html_message, from_email, recipient_list, fail_silently=False, connection=None):
    text_message = generate_plain_text(html_message)

    msg = EmailMultiAlternatives(subject, text_message, from_email, recipient_list, connection=connection)
    msg.attach_alternative(html_message, "text/html")
    msg.send(fail_silently=fail_silently)
