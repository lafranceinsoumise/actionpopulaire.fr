from django import template
from django.template import TemplateSyntaxError
from django.template.base import kwarg_re, Node
from django.utils.html import conditional_escape

register = template.Library()


def parse_global_url(parser, token):
    r"""
    Exactly like the url template tag, but returns fully qualified url to admin_view

    This is a way to define links that aren't tied to a particular URL
    configuration::

        {% url "url_name" arg1 arg2 %}

        or

        {% url "url_name" name1=value1 name2=value2 %}

    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(
            "'%s' takes at least one argument, a URL pattern name." % bits[0]
        )
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == "as":
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to url tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))

    return (viewname, args, kwargs, asvar)


class GlobalURLNode(Node):
    def __init__(self, view_name, args, kwargs, asvar, url_function):
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar
        self.url_function = url_function

    def render(self, context):
        from django.urls import NoReverseMatch

        args = [arg.resolve(context) for arg in self.args]
        kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}
        view_name = self.view_name.resolve(context)

        url = ""
        try:
            url = self.url_function(view_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            if self.asvar is None:
                raise

        if self.asvar:
            context[self.asvar] = url
            return ""
        else:
            if context.autoescape:
                url = conditional_escape(url)
            return url


@register.tag
def admin_url(parser, token):
    from agir.lib.admin.utils import admin_url

    return GlobalURLNode(*parse_global_url(parser, token), url_function=admin_url)


@register.tag
def front_url(parser, token):
    from ..utils import front_url

    return GlobalURLNode(*parse_global_url(parser, token), url_function=front_url)
