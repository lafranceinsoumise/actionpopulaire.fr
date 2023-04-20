from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html

from agir.groups.models import Membership
from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter
from agir.lib.admin.form_fields import AutocompleteSelectModel
from agir.mailing.models import Segment


class SegmentFilter(AutocompleteRelatedModelFilter):
    title = "segment"
    parameter_name = "segment"

    def get_rendered_widget(self):
        widget = AutocompleteSelectModel(
            Segment,
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
        ) + format_html(
            '<a style="margin-top: 5px" href="{}">Gérer les segments</a>',
            reverse("admin:mailing_segment_changelist"),
        )

    def get_queryset_for_field(self):
        return Segment.objects.all()

    def queryset(self, request, queryset):
        if self.value():
            try:
                s = Segment.objects.get(pk=self.value())
            except Segment.DoesNotExist:
                return queryset
            return queryset.filter(pk__in=s.get_subscribers_queryset())
        else:
            return queryset


class TagListFilter(AutocompleteRelatedModelFilter):
    field_name = "tags"
    title = "Tags"


class AnimateMoreThanOneGroup(admin.SimpleListFilter):
    title = "cette personne anime plus d'un groupe d'action"
    parameter_name = "two_or_more_groups"

    def lookups(self, request, model_admin):
        return (
            (Membership.MEMBERSHIP_TYPE_MANAGER, "Gère ou anime plus d'un groupe"),
            (Membership.MEMBERSHIP_TYPE_REFERENT, "Anime plus d'un groupe"),
            ("", ""),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.annotate(
                group_count=Count(
                    "memberships",
                    filter=Q(
                        memberships__supportgroup__published=True,
                        memberships__membership_type__gte=self.value(),
                    ),
                )
            ).filter(group_count__gt=1)
