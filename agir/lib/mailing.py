import re
from email.mime.base import MIMEBase
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import html2text
import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.http import QueryDict
from django.template import loader, TemplateDoesNotExist
from django.template.base import Template
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from agir.api.context_processors import basic_information
from agir.lib.utils import generate_token_params, front_url, AutoLoginUrl
from agir.people.models import Person

__all__ = [
    "send_template_email",
    "send_mosaico_email",
    "generate_plain_text",
    "fetch_mosaico_template",
]

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


def send_message(
    from_email,
    recipient,
    subject,
    text,
    html=None,
    reply_to=None,
    attachments=None,
    connection=None,
    headers=None,
):
    email = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=from_email,
        reply_to=reply_to,
        connection=connection,
        to=[recipient.email if isinstance(recipient, Person) else recipient],
        headers=headers,
    )
    if html is not None:
        email.attach_alternative(html, "text/html")
    if attachments is not None:
        for attachment in attachments:
            if isinstance(attachment, MIMEBase):
                email.attach(attachment)
            elif isinstance(attachment, dict):
                email.attach(**attachment)
            else:
                email.attach(*attachment)
    email.send()


def get_context_from_bindings(code, recipient, bindings):
    """Finalizes the bindings and create a Context for templating"""
    bindings = dict(bindings)

    if isinstance(recipient, Person):
        if recipient.role is not None and recipient.role.is_active:
            connection_params = generate_token_params(recipient)
            for key, value in bindings.items():
                if isinstance(value, AutoLoginUrl):
                    bindings[key] = add_params_to_urls(value, connection_params)
            bindings["merge_login"] = bindings["MERGE_LOGIN"] = urlencode(
                connection_params
            )

        bindings["email"] = bindings["EMAIL"] = recipient.email
        bindings["greetings"] = bindings["formule_adresse"] = bindings[
            "GREETINGS"
        ] = recipient.formule_adresse
        bindings["greetings_insoumise"] = bindings[
            "formule_adresse_insoumise"
        ] = recipient.formule_adresse_insoumise
    else:
        bindings["email"] = bindings["EMAIL"] = recipient

    bindings["preferences_link"] = bindings["PREFERENCES_LINK"] = front_url("contact")
    bindings["unsubscribe_link"] = bindings["UNSUBSCRIBE_LINK"] = front_url(
        "unsubscribe"
    )

    qs = QueryDict(mutable=True)
    qs.update(bindings)

    # We first initialize the LINK_BROWSER variable as "#" (same page)
    qs["LINK_BROWSER"] = "#"
    # we generate the final browser link and add it to result dictionary
    if code in settings.EMAIL_TEMPLATES:
        url = settings.EMAIL_TEMPLATES[code]
        bindings["LINK_BROWSER"] = f"{url}?{qs.urlencode()}"

    return bindings


def render_email_template(template, context):
    context = {
        **context,
        **basic_information(None),
    }
    subject = template.render(
        {
            **context,
            "email_template": Template(
                "{% autoescape off %}{% block subject %}{% endblock %}{% endautoescape %}"
            ),
        }
    ).strip()
    text_content = template.render(
        {**context, "email_template": "mail_templates/layout.txt"}
    ).strip()
    html_content = template.render(
        {**context, "email_template": "mail_templates/layout.html"}
    )

    return subject, text_content, html_content


def send_template_email(
    template_name,
    recipients,
    from_email=settings.EMAIL_FROM,
    bindings=None,
    connection=None,
    backend=None,
    reply_to=None,
    attachments=None,
    headers=None,
):
    template = get_template(template_name)

    if connection is None:
        connection = get_connection(backend)

    with connection:
        for recipient in recipients:
            if getattr(recipient, "role", None) and not recipient.role.is_active:
                continue

            context = get_context_from_bindings(None, recipient, bindings)
            subject, text, html = render_email_template(template, context)

            send_message(
                from_email=from_email,
                recipient=recipient,
                subject=subject,
                text=text,
                html=html,
                reply_to=reply_to,
                attachments=attachments,
                connection=connection,
                headers=headers,
            )


def send_mosaico_email(
    code,
    subject,
    from_email,
    recipients,
    bindings=None,
    connection=None,
    backend=None,
    reply_to=None,
    attachments=None,
    headers=None,
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

    if hasattr(recipients, "as_email_recipients"):
        recipients = recipients.as_email_recipients()
    elif isinstance(recipients, str):
        recipients = [recipients]
    else:
        try:
            iter(recipients)
        except TypeError:
            recipients = [recipients]

    if bindings is None:
        bindings = {}

    if connection is None:
        connection = get_connection(backend)

    html_template = loader.get_template(f"mail_templates/{code}.html")
    try:
        text_template = loader.get_template(f"mail_templates/{code}.txt")
    except TemplateDoesNotExist:
        text_template = None

    with connection:
        for recipient in recipients:
            # recipient can be either a Person or an email address
            if getattr(recipient, "role", None) and not recipient.role.is_active:
                continue

            context = get_context_from_bindings(code, recipient, bindings)
            html_message = html_template.render(context=context)
            text_message = (
                text_template.render(
                    context={k: conditional_html_to_text(v) for k, v in context.items()}
                )
                if text_template
                else generate_plain_text(html_message)
            )

            if hasattr(recipient, "email"):
                recipient_email = recipient.email
            else:
                recipient_email = recipient

            send_message(
                from_email=from_email,
                recipient=recipient_email,
                subject=subject,
                text=text_message,
                html=html_message,
                reply_to=reply_to,
                connection=connection,
                attachments=attachments,
                headers=headers,
            )


def fetch_mosaico_template(url):
    res = requests.get(url)
    res.raise_for_status()

    return MOSAICO_VAR_REGEX.sub(r"{{ \1 }}", res.text)
