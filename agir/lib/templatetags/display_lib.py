from django import template

from ..display import (
    display_price,
    pretty_time_since as original_pretty_time_since,
    genrer as original_genrer,
)

register = template.Library()


@register.filter(name="display_price_in_cent")
def display_price_in_cent(value):
    if isinstance(value, str):
        return value
    return display_price(value, price_in_cents=True)


@register.filter(name="display_price_in_unit")
def display_price_in_unit(value):
    if isinstance(value, str):
        return value
    return display_price(value, price_in_cents=False)


@register.filter(name="pretty_time_since")
def pretty_time_since(d, now=None):
    return original_pretty_time_since(d, now)


@register.tag(name="genrer")
def parse_genrer(parser, token):
    bits = token.split_contents()

    if len(bits) < 2 or len(bits) > 5:
        raise template.TemplateSyntaxError(
            "Le tag %r prend entre 1 et 4 arguments" % bits[0]
        )

    if len(bits) in [2, 4]:
        values = bits[1:]
        genre = None
    else:
        *values, genre = bits[1:]
        genre = parser.compile_filter(genre)

    return GenrerNode([parser.compile_filter(v) for v in values], genre=genre)


class GenrerNode(template.Node):
    def __init__(self, values, *args, genre=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = values
        self.genre = genre

    def render(self, context):
        values = [v.resolve(context) for v in self.values]
        if self.genre:
            genre = self.genre.resolve(context)
        else:
            genre = context["gender"]

        return original_genrer(genre, *values)
