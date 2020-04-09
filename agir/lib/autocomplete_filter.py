from django.contrib.admin.widgets import AutocompleteSelect
from django import forms
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields.related_descriptors import (
    ReverseManyToOneDescriptor,
    ManyToManyDescriptor,
)
from django.forms.widgets import Media, MEDIA_TYPES


class SelectModelFilter(admin.SimpleListFilter):
    template = "custom_fields/autocomplete-filter.html"
    field_name = ""
    field_pk = "pk"
    widget_attrs = {}
    form_field = forms.ModelChoiceField

    def __init__(self, request, params, model, model_admin):
        self.qs_filter_key = "{}__{}__exact".format(self.field_name, self.field_pk)
        self.parameter_name = self.parameter_name or self.field_name.replace("__", "-")
        self.model_admin = model_admin
        super().__init__(request, params, model, model_admin)

        self.model = model

        field_name_parts = self.field_name.split("__")

        for part in field_name_parts[:-1]:
            model = model._meta.get_field(
                part
            ).remote_field.model  # saute vers le modèle suivant

        self.rendered_widget = self.make_rendered_widget(model, field_name_parts[-1])

    def make_rendered_widget(self, model, field_name):
        widget = forms.Select()
        FieldClass = self.get_form_field()
        field = FieldClass(
            queryset=self.get_queryset_for_field(model, field_name),
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

    def get_queryset_for_field(self, model, name):
        field_desc = getattr(model, name)
        if isinstance(field_desc, ManyToManyDescriptor):
            related_model = (
                field_desc.rel.related_model
                if field_desc.reverse
                else field_desc.rel.model
            )
        elif isinstance(field_desc, ReverseManyToOneDescriptor):
            related_model = field_desc.rel.related_model
        else:
            return field_desc.get_queryset()
        return related_model.objects.get_queryset()

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

    def __init__(self, request, params, model, model_admin):
        self.parameter_name = "{}__{}__exact".format(self.field_name, self.field_pk)
        super().__init__(request, params, model, model_admin)

        self.model = model

        field_name_parts = self.field_name.split("__")

        for part in field_name_parts[:-1]:
            model = model._meta.get_field(
                part
            ).remote_field.model  # saute vers le modèle suivant

    def make_rendered_widget(self, model, field_name):
        rel = model._meta.get_field(field_name).remote_field

        widget = AutocompleteSelect(rel, self.model_admin.admin_site,)
        FieldClass = self.get_form_field()
        field = FieldClass(
            queryset=self.get_queryset_for_field(model, field_name),
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
