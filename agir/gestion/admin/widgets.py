from django import forms
from django.conf import settings
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.utils.translation import get_language


class HierarchicalSelect(forms.Select):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )

        level = value.count("-") + 1
        current_class = (" " + option["attrs"].get("class", "")).strip()
        option["attrs"]["class"] = f"l{level}{current_class}"

        return option

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        css_class = (" " + context["widget"]["attrs"].get("class", "")).strip()
        context["widget"]["attrs"]["class"] = f"hierarchical-select{css_class}"

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
            + ("admin/js/jquery.init.js", "admin/gestion/hierarchical-select.js"),
            css={
                "screen": ("admin/css/vendor/select2/select2%s.css" % extra,),
            },
        )
