from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import loader

import html2text

from people.models import Person
from front.utils import generate_token_params, front_url, is_front_url

__all__ = ['send_mail', 'send_mosaico_email']

_h = html2text.HTML2Text()
_h.ignore_images = True


def generate_plain_text(html_message):
    return _h.handle(html_message)


def add_params_to_urls(url, params):
    parts = urlsplit(url)
    query = parse_qsl(parts.query)
    query.extend(params.items())
    return urlunsplit([parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment])


def get_context_from_bindings(code, recipient, bindings):
    """Finalizes the bindings and create a Context for templating
    """
    if code not in settings.EMAIL_TEMPLATES:
        raise ImproperlyConfigured("Mail '%s' cannot be found")

    url = settings.EMAIL_TEMPLATES[code]

    res = dict(bindings)
    res['EMAIL'] = recipient

    qs = QueryDict(mutable=True)
    qs.update(res)

    # We first initialize the LINK_BROWSER variable as "#" (same page)
    qs['LINK_BROWSER'] = "#"
    # we generate the final browser link and add it to result dictionary
    res['LINK_BROWSER'] = f"{url}?{qs.urlencode()}"

    return res


def send_mosaico_email(code, subject, from_email, recipients, bindings=None, connection=None, backend=None,
                       fail_silently=False, preferences_link=True):
    """Send an email from a Mosaico template

    :param code: the code identifying the Mosaico template
    :param subject: the subject line of the email
    :param from_email: the address from which the email is to be sent
    :param recipients: a list of recipients to which the email will be send; alternatively, a single address
    :param bindings: a dictionary of replacements variables and their target values in the Mosaico template
    :param connection: an optional email server connection to use to send the emails
    :param backend: if no connection is given, an optional mail backend to use to send the emails
    :param fail_silently: whether any error should be raised, or just be ignored; by default it will raise
    :param gen_connection_params_function: a function that takes a recipient and generates connection params
    """
    if isinstance(recipients, Person):
        recipients = [recipients]

    if bindings is None:
        bindings = {}

    if connection is None:
        connection = get_connection(backend, fail_silently)

    if preferences_link:
        bindings['PREFERENCES_LINK'] = front_url('message_preferences')

    link_bindings = {key: value for key, value in bindings.items() if is_front_url(value)}

    template = loader.get_template(f'mail_templates/{code}.html')

    for recipient in recipients:
        if link_bindings:
            connection_params = generate_token_params(recipient)
            for key, value in link_bindings.items():
                bindings[key] = add_params_to_urls(value, connection_params)

        context = get_context_from_bindings(code, recipient, bindings)

        html_message = template.render(context=context)
        text_message = generate_plain_text(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=from_email,
            to=[recipient.email],
            connection=connection
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=fail_silently)


def send_mail(subject, html_message, from_email, recipient_list, fail_silently=False, connection=None):
    text_message = generate_plain_text(html_message)

    address_list = [recipient.email for recipient in recipient_list]

    msg = EmailMultiAlternatives(subject, text_message, from_email, address_list, connection=connection)
    msg.attach_alternative(html_message, "text/html")
    msg.send(fail_silently=fail_silently)
