from django import template
from django.utils.safestring import mark_safe
import datetime

register = template.Library()


@register.tag
def query_string(parser, token):
    """
    Allows you too manipulate the query string of a page by adding and removing keywords.
    If a given value is a context variable it will resolve it.

    TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    )
    """

    try:
        tag_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" % token.contents.split()[0]
        )
    if not (add_string[0] == add_string[-1] and add_string[0] in ('"', "'")) or not (
        remove_string[0] == remove_string[-1] and remove_string[0] in ('"', "'")
    ):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )

    add = string_to_dict(add_string[1:-1])
    remove = string_to_list(remove_string[1:-1])

    return QueryStringNode(add, remove)
