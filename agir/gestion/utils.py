from django.utils.html import format_html


def lien(href, label):
    return format_html('<a href="{}">{}</a>', href, label)
