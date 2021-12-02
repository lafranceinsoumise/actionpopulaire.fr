from django import forms
from django.contrib import admin
from django.contrib.admin.utils import get_fields_from_path
from django.contrib.admin.widgets import AutocompleteSelect
from django.core.exceptions import ImproperlyConfigured
from django.forms.widgets import Media, MEDIA_TYPES


class SelectModelFilter(admin.SimpleListFilter):
    template = "custom_fields/autocomplete-filter.html"
    field_name = ""
    field_pk = "pk"
    widget_attrs = {}
    form_field = forms.ModelChoiceField

    def __init__(self, request, params, model, model_admin):
        self.parameter_name = self.parameter_name or self.field_name.replace("__", "-")
        super().__init__(request, params, model, model_admin)

        self.model_admin = model_admin
        self.qs_filter_key = "{}__{}__exact".format(self.field_name, self.field_pk)
        self.model = model
        self.rendered_widget = self.get_rendered_widget()

    def get_rendered_widget(self):
        widget = forms.Select()
        FieldClass = self.get_form_field()
        field = FieldClass(
            queryset=self.get_queryset_for_field(),
            widget=widget,
            required=False,
        )

        attrs = self.widget_attrs.copy()
        attrs["id"] = "id-%s-autocomplete-filter" % self.field_name
        attrs["class"] = f'{attrs.get("class", "")} select-filter'.strip()
        return field.widget.render(
            name=self.parameter_name,
            value=self.used_parameters.get(self.parameter_name, ""),
            attrs=attrs,
        )

    def get_queryset_for_field(self):
        fields = get_fields_from_path(self.model, self.field_name)
        model = fields[-1].remote_field.model
        return model._default_manager.all()

    def get_form_field(self):
        """Return the type of form field to be used."""
        return self.form_field

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.qs_filter_key: self.value()})
        else:
            return queryset


class AutocompleteFilter(SelectModelFilter):
    template = "custom_fields/autocomplete-filter.html"
    field_name = ""
    field_pk = "pk"
    widget_attrs = {}
    form_field = forms.ModelChoiceField

    class Media:
        js = (
            "admin/js/jquery.init.js",
            "lib/autocomplete-filter.js",
        )
        css = {
            "screen": ("lib/autocomplete-filter.css",),
        }

    def get_rendered_widget(self):
        rel = get_fields_from_path(self.model, self.field_name)[-1].remote_field
        widget = AutocompleteSelect(
            rel,
            self.model_admin.admin_site,
        )
        FieldClass = self.get_form_field()
        field = FieldClass(
            queryset=self.get_queryset_for_field(),
            widget=widget,
            required=False,
        )

        self._add_media(self.model_admin, widget)

        attrs = self.widget_attrs.copy()
        attrs["id"] = "id-%s-autocomplete-filter" % self.field_name
        attrs["class"] = f'{attrs.get("class", "")} select-filter'.strip()

        return field.widget.render(
            name=self.parameter_name,
            value=self.used_parameters.get(self.parameter_name, ""),
            attrs=attrs,
        )

    def _add_media(self, model_admin, widget):

        if not hasattr(model_admin, "Media"):
            raise ImproperlyConfigured(
                "Add empty Media class to %s. Sorry about this bug." % model_admin
            )

        def _get_media(obj):
            return Media(media=getattr(obj, "Media", None))

        media = (
            _get_media(model_admin)
            + widget.media
            + _get_media(AutocompleteFilter)
            + _get_media(self)
        )

        for name in MEDIA_TYPES:
            setattr(model_admin.Media, name, getattr(media, "_" + name))
