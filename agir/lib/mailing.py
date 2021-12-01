from email.mime.base import MIMEBase
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import html2text
import re
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives, get_connection
from django.http import QueryDict
from django.template import loader, TemplateDoesNotExist
from django.utils.safestring import mark_safe

from agir.lib.utils import generate_token_params, front_url, is_front_url, AutoLoginUrl
from agir.people.models import Person

__all__ = ["send_mosaico_email", "generate_plain_text", "fetch_mosaico_template"]

MOSAICO_VAR_REGEX = re.compile(r"\[([-A-Z_]+)\]")

_h = html2text.HTML2Text(bodywidth=0)
_h.ignore_images = True
_h.ignore_tables = True


def conditional_html_to_text(text):
    if hasattr(text, "__html__"):
        return mark_safe(_h.handle(text))
    return mark_safe(text)


def generate_plain_text(html_message):
    return (
        re.sub("Cet email a été envoyé à .*$", "", _h.handle(html_message))
        + """
------------------------------------------------------------------
Cet email a été envoyé à {{ EMAIL }}. Il est personnel, ne le transférez pas.

>> Choisir les emails que vous recevez
{{ preferences_link }}

>> Arrêter complètement de recevoir des emails
{{ unsubscribe_link }}
"""
    )


def add_params_to_urls(url, params):
    parts = urlsplit(url)
    query = parse_qsl(parts.query)
    query.extend(params.items())
    return urlunsplit(
        [parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment]
    )


def get_context_from_bindings(code, recipient, bindings):
    """Finalizes the bindings and create a Context for templating"""
    if code not in settings.EMAIL_TEMPLATES:
        raise ImproperlyConfigured("Mail '%s' cannot be found")

    url = settings.EMAIL_TEMPLATES[code]

    res = dict(bindings)

    if isinstance(recipient, Person):
        res["email"] = res["EMAIL"] = recipient.email
        res["greetings"] = res["formule_adresse"] = res[
            "GREETINGS"
        ] = recipient.formule_adresse
        res["greetings_insoumise"] = res[
            "formule_adresse_insoumise"
        ] = recipient.formule_adresse_insoumise
    else:
        res["email"] = res["EMAIL"] = recipient

    qs = QueryDict(mutable=True)
    qs.update(res)

    # We first initialize the LINK_BROWSER variable as "#" (same page)
    qs["LINK_BROWSER"] = "#"
    # we generate the final browser link and add it to result dictionary
    res["LINK_BROWSER"] = f"{url}?{qs.urlencode()}"

    return res


def send_mosaico_email(
    code,
    subject,
    from_email,
    recipients,
    recipient_type="to",
    bindings=None,
    connection=None,
    backend=None,
    fail_silently=False,
    preferences_link=True,
    reply_to=None,
    attachments=None,
):
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
    try:
        iter(recipients)
    except TypeError:
        recipients = [recipients]

    if recipient_type not in ["to", "cc", "bcc"]:
        raise ValueError("`recipient_type` must be to, cc or bcc")

    if bindings is None:
        bindings = {}

    if connection is None:
        connection = get_connection(backend, fail_silently)

    if preferences_link:
        bindings["preferences_link"] = bindings["PREFERENCES_LINK"] = front_url(
            "contact"
        )
        bindings["unsubscribe_link"] = bindings["UNSUBSCRIBE_LINK"] = front_url(
            "unsubscribe"
        )

    link_bindings = {
        key: value for key, value in bindings.items() if is_front_url(value)
    }

    html_template = loader.get_template(f"mail_templates/{code}.html")
    try:
        text_template = loader.get_template(f"mail_templates/{code}.txt")
    except TemplateDoesNotExist:
        text_template = None

    with connection:
        for recipient in recipients:
            # recipient can be either a Person or an email address
            if isinstance(recipient, Person):
                if recipient.role is not None and not recipient.role.is_active:
                    continue
                connection_params = generate_token_params(recipient)
                for key, value in link_bindings.items():
                    if isinstance(value, AutoLoginUrl):
                        bindings[key] = add_params_to_urls(value, connection_params)
                bindings["MERGE_LOGIN"] = urlencode(connection_params)

            context = get_context_from_bindings(code, recipient, bindings)
            html_message = html_template.render(context=context)
            text_message = (
                text_template.render(
                    context={k: conditional_html_to_text(v) for k, v in context.items()}
                )
                if text_template
                else generate_plain_text(html_message)
            )

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=from_email,
                reply_to=reply_to,
                connection=connection,
                **{
                    recipient_type: [
                        recipient.email if isinstance(recipient, Person) else recipient
                    ]
                },
            )
            email.attach_alternative(html_message, "text/html")
            if attachments is not None:
                for attachment in attachments:
                    if isinstance(attachment, MIMEBase):
                        email.attach(attachment)
                    elif isinstance(attachment, dict):
                        email.attach(**attachment)
                    else:
                        email.attach(*attachment)
            email.send(fail_silently=fail_silently)


def fetch_mosaico_template(url):
    res = requests.get(url)
    res.raise_for_status()

    return MOSAICO_VAR_REGEX.sub(r"{{ \1 }}", res.text)
