from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

from django import template


register = template.Library()


class PaginationNode(template.Node):
    context_key = "__pagination_context"

    def __init__(self, page_obj, pages_around, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_obj = page_obj
        self.pages_around = pages_around

    def render(self, context):
        page_obj = self.page_obj.resolve(context)
        cache = context.render_context.setdefault(self.context_key, {})

        if page_obj not in cache:
            template = context.template.engine.get_template("lib/pagination.html")
            request = context["request"]

            with context.push(
                base_url=self.get_base_url(request.get_full_path()),
                page_obj=page_obj,
                **self.get_page_params(page_obj)
            ):
                cache[page_obj] = template.render(context)

        return cache[page_obj]

    def get_base_url(self, url):
        url = urlparse(url)
        query = parse_qs(url.query)
        query.pop("page", None)
        base_url = urlunparse(url._replace(query=urlencode(query, True)))
        if query:
            base_url += "&"
        else:
            base_url += "?"
        return base_url

    def get_page_params(self, page_obj):
        num_pages = page_obj.paginator.num_pages

        start, end = (
            max(2, page_obj.number - self.pages_around),
            min(num_pages - 1, page_obj.number + self.pages_around),
        )

        if start == 2:
            start = 1
            show_first_page = False
        else:
            show_first_page = True

        if end == num_pages - 1:
            end = num_pages
            show_last_page = False
        else:
            show_last_page = True

        return {
            "page_range": range(start, end + 1),
            "show_first_page": show_first_page,
            "show_last_page": show_last_page,
        }


@register.tag(name="pagination")
def do_pagination(parser, token):
    """Affiche des liens de pagination"""
    bits = token.split_contents()

    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "Le tag %r prend au moins un argument : l'objet de page dont"
            " il faut afficher la pagination" % bits[0]
        )

    page_obj = parser.compile_filter(bits[1])

    if len(bits) == 2:
        pages_around = 4
    else:
        if len(bits) > 3:
            raise template.TemplateSyntaxError(
                "Le tag %r prend au maximum deux arguments : l'objet de page et "
                " le nombre de pages à afficher autour de la page actuelle."
            )

        pages_around = parser.compile_filter(bits[2])

    return PaginationNode(page_obj, pages_around=pages_around)
