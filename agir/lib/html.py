import dataclasses
import re
from abc import ABC
from functools import partial
from html import unescape
from html.parser import HTMLParser
from typing import Dict

import bleach
from django.conf import settings
from django.utils.html import mark_safe, strip_tags


def sanitize_html(text, tags=None):
    attributes = bleach.ALLOWED_ATTRIBUTES
    if tags is None:
        tags = settings.USER_ALLOWED_TAGS
    if "img" in tags:
        attributes = {**attributes, "img": ["src", "alt", "width", "height"]}
    return mark_safe(
        bleach.clean(str(text), tags=tags, attributes=attributes, strip=True)
    )


def textify(html):
    # Remove html tags and continuous whitespaces
    text_only = re.sub("[ \t]+", " ", strip_tags(html))
    # Strip single spaces in the beginning of each line
    return text_only.replace("\n ", "\n").strip()


@dataclasses.dataclass
class Tag:
    name: str
    attrs: dict


SPACES_RE = re.compile("\s+")
DUP_SPACES_RE = re.compile(r"\s+(\s)")


def remove_duplicate_spaces(text):
    return DUP_SPACES_RE.sub(r"\1", text)


def format_link(href, text):
    text = text.strip()
    return f">> {text[0].upper()}{text[1:]}\n{href}"


def handle_paragraph(tag, text, context):
    links = context.pop("links", None)
    text = text.strip()

    if links:
        text += "\n\n" + "\n\n".join(format_link(*l) for l in links)

    return f"\n{text}\n"


def handle_linebreak(tag, text, context):
    return f"\n{text.lstrip()}"


def handle_link(tag, text, context):
    href = tag.attrs.get("href")
    if href:
        context.setdefault("links", []).append((href, text))
    return text


def handle_italic(tag, text, context):
    return f"*{text}*"


def handle_bold(tag, text, context):
    return f"**{text}**"


def handle_title(tag, text, context, sep):
    return f"\n{text}\n{sep * len(text)}\n"


TAGS = {
    "p": handle_paragraph,
    "div": handle_paragraph,
    "a": handle_link,
    "i": handle_italic,
    "em": handle_italic,
    "b": handle_bold,
    "strong": handle_bold,
    "h1": partial(handle_title, sep="#"),
    "h2": partial(handle_title, sep="="),
    "h3": partial(handle_title, sep="-"),
    "h4": partial(handle_title, sep="_"),
    "br": handle_linebreak,
}


class HTMLFilter(HTMLParser, ABC):
    """
    A simple no dependency HTML -> TEXT converter.
    Usage:
          str_output = HTMLFilter.convert_html_to_text(html_input)
    """

    def __init__(self, *args, **kwargs):
        self.tag_stack = []
        self.context = {}
        self.text = [""]
        self.links = []
        super().__init__(*args, convert_charrefs=True, **kwargs)

    def handle_starttag(self, tag: str, attrs: Dict[str, str]):
        self.push_tag(tag, attrs)

    def handle_endtag(self, tag):
        tag = tag.lower()
        prev_tag_name = None
        while prev_tag_name != tag:
            prev_tag = self.pop_tag()
            prev_tag_name = prev_tag.name

    def handle_data(self, data):
        # on remplace tout espacement par un espace simple.
        self.text[-1] += SPACES_RE.sub(" ", data)

    def push_tag(self, tag, attrs):
        self.tag_stack.append(Tag(tag.lower(), dict(attrs)))
        self.text.append("")

    def pop_tag(self):
        tag = self.tag_stack.pop()
        text = self.text.pop()
        if tag.name in TAGS:
            self.text[-1] += TAGS[tag.name](tag, text, self.context)
        else:
            self.text[-1] += text
        return tag

    def close(self) -> None:
        super().close()

        while self.tag_stack:
            self.pop_tag()

    @classmethod
    def convert_html_to_text(cls, html: str) -> str:
        f = cls()
        f.feed(html)
        f.close()

        return "".join(f.text).strip()


def html_to_text(html):
    return HTMLFilter.convert_html_to_text(html)
