from urllib.parse import urljoin

from django.conf import settings
from django.db.models import Model
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from agir.lib.http import add_query_params_to_url


def get_admin_link(instance):
    return reverse(
        f"admin:{instance._meta.app_label}_{instance._meta.model_name}_change",
        args=(instance.pk,),
    )


def display_list_of_links(links):
    """Retourne une liste de liens à afficher dans l'admin Django

    :param links: un itérateur de tuples (link_target, link_text) ou (model_instance, link_text)
    :return: le code html de la liste de liens
    """
    links = (
        (
            get_admin_link(link_or_instance)
            if isinstance(link_or_instance, Model)
            else link_or_instance,
            text,
        )
        for link_or_instance, text in links
    )
    return format_html_join(mark_safe("<br>"), '<a href="{}">{}</a>', links)


def admin_url(viewname, args=None, kwargs=None, query=None, absolute=True):
    if not viewname.startswith("admin:"):
        viewname = f"admin:{viewname}"

    url = reverse(viewname, args=args, kwargs=kwargs, urlconf="agir.api.admin_urls")
    if absolute:
        url = urljoin(settings.API_DOMAIN, url)
    if query:
        url = add_query_params_to_url(url, query)
    return url
