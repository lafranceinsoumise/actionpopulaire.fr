from django import template

from agir.lib.html import html_to_text

register = template.Library()


@register.filter("html_to_text")
def html_to_text_filter(text):
    return html_to_text(text)
