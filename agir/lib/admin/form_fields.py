import json

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS, AutocompleteSelect
from django.db import models
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
        css_class = (
            f'with-suggestions {context["widget"]["attrs"].get("class", "")}'.strip()
        )
        context["widget"]["attrs"]["class"] = css_class

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


class AdminJsonWidget(forms.Textarea):
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


class CleavedDateInput(forms.DateInput):
    def __init__(self, attrs=None, format=None, *, today_button=True):
        super().__init__(attrs, format)
        self._today_button = today_button

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        css_class = (
            f'cleaved-date-input {context["widget"]["attrs"].get("class", "")}'.strip()
        )
        context["widget"]["attrs"]["class"] = css_class
        if self._today_button:
            context["widget"]["attrs"]["data-today"] = "true"

        return context

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"

        return forms.Media(
            js=(
                "admin/js/vendor/jquery/jquery%s.js" % extra,
                "admin/js/vendor/cleave.min.js",
                "admin/js/cleaved-date-input.js",
            ),
        )


class AutocompleteSelectModel(AutocompleteSelect):
    dummies = {}

    def __init__(self, model=None, *args, **kwargs):
        # AutocompleteSelect normally works only with a model class foreign key related
        # field. The following is a convoluted way to make it work with a model class
        # that is not a foreign key related field of another
        class Meta:
            app_label = model._meta.app_label
            proxy = True
            managed = False

        dummy_name = f"Dummy{model.__name__}"
        if dummy_name not in self.dummies:
            self.dummies[dummy_name] = type(
                dummy_name,
                (model,),
                {
                    "__module__": self.__module__,
                    "self": models.ForeignKey(
                        to=model, on_delete=models.DO_NOTHING, related_name="+"
                    ),
                    "Meta": Meta,
                },
            )
        super().__init__(
            self.dummies[dummy_name]._meta.get_field("self"), *args, **kwargs
        )
