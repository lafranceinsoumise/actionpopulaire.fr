from django import template

from ..display import display_price as original_display_price

register = template.Library()


@register.filter(name='display_price')
def display_price(value):
    return original_display_price(value)
