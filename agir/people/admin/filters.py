from django.contrib import admin
from django.db.models import Count, Q, Exists, OuterRef
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from agir.groups.models import Membership, SupportGroup
from agir.lib.admin.autocomplete_filter import (
    AutocompleteRelatedModelFilter,
    AutocompleteSelectModelBaseFilter,
)
from agir.lib.admin.form_fields import AutocompleteSelectModel
from agir.mailing.models import Segment
from agir.people.models import PersonQualification, PersonEmail, Role, Person


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
            return queryset.filter(pk__in=s.get_people())
        else:
            return queryset


class BouncedEmailFilter(admin.SimpleListFilter):
    title = "adresse email"
    parameter_name = "bounced_email"

    def lookups(self, request, model_admin):
        return (
            ("1", "Pas d'adresse e-mail valide"),
            ("0", "Au moins une adresse e-mail valide"),
            ("", ""),
        )

    def queryset(self, request, queryset):
        if self.value() in ("0", "1"):
            has_valid = self.value() == "0"
            return queryset.annotate(
                has_valid=Exists(
                    PersonEmail.objects.filter(person_id=OuterRef("id")).filter(
                        _bounced=False
                    )
                )
            ).filter(has_valid=has_valid)

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


class QualificationListFilter(AutocompleteRelatedModelFilter):
    field_name = "qualification"
    title = "type de statut"


class PersonQualificationStatusListFilter(admin.SimpleListFilter):
    title = "état du statut"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return PersonQualification.Status.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.only_statuses(statuses=[self.value()])
        return queryset


class PersonQualificationSupportGroupListFilter(AutocompleteSelectModelBaseFilter):
    title = "groupe d'action"
    filter_model = SupportGroup
    parameter_name = "supportgroup"

    def get_queryset_for_field(self):
        return SupportGroup.objects.all()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supportgroup_id=self.value())
        else:
            return queryset


class PersonAccountActivateListFilter(admin.SimpleListFilter):
    title = "compte activé ou non"
    parameter_name = "disabled_account"

    def lookups(self, request, model_admin):
        return (("enabled", _("Activé")), ("disabled", _("Désactivé")))

    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            is_enabled=Exists(
                Person.objects.filter(role_id=OuterRef("role__id")).filter(
                    role__is_active=True
                )
            )
        )

        if self.value() == "enabled":
            return queryset.filter(is_enabled=True)
        if self.value() == "disabled":
            return queryset.exclude(is_enabled=True)
