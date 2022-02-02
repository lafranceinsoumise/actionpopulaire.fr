import json

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.forms import Textarea
from django.utils.translation import get_language


class SuggestingTextInput(forms.TextInput):
    def __init__(self, suggestions=(), attrs=None):
        super().__init__(attrs=attrs)
        self.suggestions = suggestions

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault("data-suggestions", json.dumps(self.suggestions))
        return attrs

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        css_class = (" " + context["widget"]["attrs"].get("class", "")).strip()
        context["widget"]["attrs"]["class"] = f"with-suggestions{css_class}"

        return context

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        i18n_name = SELECT2_TRANSLATIONS.get(get_language())
        i18n_file = (
            ("admin/js/vendor/select2/i18n/%s.js" % i18n_name,) if i18n_name else ()
        )
        return forms.Media(
            js=(
                "admin/js/vendor/jquery/jquery%s.js" % extra,
                "admin/js/vendor/select2/select2.full%s.js" % extra,
            )
            + i18n_file
            + ("admin/js/jquery.init.js", "admin/js/with-suggestions.js"),
            css={
                "screen": ("admin/css/vendor/select2/select2%s.css" % extra,),
            },
        )


class AdminJsonWidget(Textarea):
    admin = True
    template_name = "custom_fields/admin_json.html"
    schema = None

    def __init__(self, schema=None, attrs=None):
        self.schema = schema
        default_attrs = {"class": "jsoneditor"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["widget"]["schema"] = self.schema
        return context
