from datetime import timedelta

from django.contrib import admin
from django.contrib.admin import TabularInline
from django.urls import reverse, path
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter
from agir.lib.utils import front_url, shorten_url
from agir.voting_proxies.admin.actions import fulfill_voting_proxy_requests
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest


class CommuneListFilter(AutocompleteRelatedModelFilter):
    field_name = "commune"
    title = "commune"


class ConsulateListFilter(AutocompleteRelatedModelFilter):
    field_name = "consulate"
    title = "consulat"


class HasVotingProxyRequestsListFilter(admin.SimpleListFilter):
    title = "cette personne a au moins une procuration"
    parameter_name = "voting_proxy_requests"

    def lookups(self, request, model_admin):
        return (
            ("1", "Oui"),
            ("0", "Non"),
        )

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(voting_proxy_requests__isnull=True)
        if self.value() == "1":
            return queryset.filter(voting_proxy_requests__isnull=False)
        return queryset


class IsAvailableForVotingDateListFilter(admin.SimpleListFilter):
    title = "date de disponibilité"
    parameter_name = "voting_date"

    def lookups(self, request, model_admin):
        return VotingProxy.VOTING_DATE_CHOICES

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(voting_dates__contains=[self.value()])
        return queryset


class IsAvailableForMatchingListFilter(admin.SimpleListFilter):
    title = "cette personne peut recevoir une proposition"
    parameter_name = "is_available_for_matching"

    def lookups(self, request, model_admin):
        return (
            ("1", "Oui"),
            ("0", "Non"),
        )

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.exclude(
                pk__in=queryset.filter(
                    status__in=(
                        VotingProxy.STATUS_CREATED,
                        VotingProxy.STATUS_AVAILABLE,
                    ),
                )
                .exclude(last_matched__date__gt=timezone.now() - timedelta(days=2))
                .values_list("pk", flat=True)
            )
        if self.value() == "1":
            return queryset.filter(
                status__in=(VotingProxy.STATUS_CREATED, VotingProxy.STATUS_AVAILABLE),
            ).exclude(last_matched__date__gt=timezone.now() - timedelta(days=2))

        return queryset


class VoterModelAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "commune_consulate",
        "created__date",
        "status",
    )
    list_filter = (
        "status",
        CommuneListFilter,
        ConsulateListFilter,
    )
    autocomplete_fields = ("commune", "consulate")
    readonly_fields = ("created",)

    search_fields = ["email", "commune__search", "consulate__nom", "consulate__search"]

    def created__date(self, instance):
        return instance.created.date()

    created__date.short_description = "date de création"
    created__date.admin_order_field = "created"

    def commune_consulate(self, instance):
        if instance.commune is not None:
            return instance.commune
        return instance.consulate

    commune_consulate.short_description = "commune / consulat"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("commune", "consulate")

    class Media:
        pass


class InlineVotingProxyRequestAdmin(TabularInline):
    verbose_name = "Procuration acceptée"
    verbose_name_plural = "Procurations acceptées"
    extra = 0
    show_change_link = True
    model = VotingProxyRequest
    fields = (
        "full_name",
        "voting_date",
        "status",
        "created",
    )
    readonly_fields = (
        "full_name",
        "voting_date",
        "status",
        "created",
    )

    def full_name(self, instance):
        return f"{instance.first_name} {instance.last_name.upper()}"

    full_name.short_description = "mandataire"
    full_name.admin_order_field = "last_name"

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VotingProxy)
class VotingProxyAdmin(VoterModelAdmin):
    list_display = (
        *VoterModelAdmin.list_display,
        "voting_dates",
        "confirmed_dates",
        "person_link",
    )
    list_filter = (
        *VoterModelAdmin.list_filter,
        IsAvailableForVotingDateListFilter,
        HasVotingProxyRequestsListFilter,
        IsAvailableForMatchingListFilter,
    )

    inlines = [InlineVotingProxyRequestAdmin]
    readonly_fields = (*VoterModelAdmin.readonly_fields, "last_matched")
    autocomplete_fields = (
        *VoterModelAdmin.autocomplete_fields,
        "person",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("person")
            .prefetch_related("voting_proxy_requests")
        )

    def person_link(self, instance):
        if instance.person is None:
            return "-"
        href = reverse("admin:people_person_change", args=(instance.person_id,))
        return mark_safe(format_html(f'<a href="{href}">{instance.person}</a>'))

    person_link.short_description = "personne"

    def confirmed_dates(self, instance):
        return [
            request.voting_date
            for request in instance.voting_proxy_requests.exclude(
                status=VotingProxyRequest.STATUS_CANCELLED
            ).only("voting_date")
        ]

    confirmed_dates.short_description = "dates acceptées"


@admin.register(VotingProxyRequest)
class VotingProxyRequestAdmin(VoterModelAdmin):
    list_display = (
        *VoterModelAdmin.list_display,
        "voting_date__date",
        "proxy_link",
    )
    list_filter = (
        *VoterModelAdmin.list_filter,
        "voting_date",
        ("proxy", admin.EmptyFieldListFilter),
    )
    readonly_fields = ("matching_buttons",)
    autocomplete_fields = (
        *VoterModelAdmin.autocomplete_fields,
        "proxy",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("proxy")

    def voting_date__date(self, voting_proxy_request):
        return voting_proxy_request.voting_date.strftime("%d %B %Y")

    voting_date__date.short_description = "date du scrutin"
    voting_date__date.admin_order_field = "voting_date"

    def proxy_link(self, voting_proxy_request):
        if voting_proxy_request.proxy is None:
            return "-"
        href = reverse(
            "admin:voting_proxies_votingproxy_change",
            args=(voting_proxy_request.proxy_id,),
        )
        return mark_safe(
            format_html(f'<a href="{href}">{voting_proxy_request.proxy}</a>')
        )

    proxy_link.short_description = "volontaire"

    def match_voting_proxy_request_view(self, request, pk):
        voting_proxy_request = VotingProxyRequest.objects.pending().filter(pk=pk)

        return fulfill_voting_proxy_requests(request, pk, voting_proxy_request)

    def match_person_voting_proxy_request_view(self, request, pk):
        voting_proxy_request = self.get_object(request, pk)
        person_voting_proxy_requests = VotingProxyRequest.objects.pending().filter(
            email=voting_proxy_request.email
        )

        return fulfill_voting_proxy_requests(request, pk, person_voting_proxy_requests)

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/match/",
                self.admin_site.admin_view(self.match_voting_proxy_request_view),
                name="votingproxies_votingproxyrequest_match_voting_proxy_request",
            ),
            path(
                "<uuid:pk>/match-all/",
                self.admin_site.admin_view(self.match_person_voting_proxy_request_view),
                name="votingproxies_votingproxyrequest_match_person_voting_proxy_requests",
            ),
        ] + super().get_urls()

    def matching_buttons(self, voting_proxy_request):
        if voting_proxy_request.status == VotingProxyRequest.STATUS_CANCELLED:
            return "-"
        elif voting_proxy_request.status == VotingProxyRequest.STATUS_CREATED:
            return format_html(
                '<p><a href="{match_voting_proxy_request}" class="button">'
                "  Chercher uniquement pour cette demande"
                "</a></p>"
                '<p style="margin-top: 4px;"><a href="{match_person_voting_proxy_requests}" class="button">'
                "  Chercher pour toutes les demandes de cette personne"
                "</a></p>",
                match_voting_proxy_request=reverse(
                    "admin:votingproxies_votingproxyrequest_match_voting_proxy_request",
                    args=(voting_proxy_request.pk,),
                ),
                match_person_voting_proxy_requests=reverse(
                    "admin:votingproxies_votingproxyrequest_match_person_voting_proxy_requests",
                    args=(voting_proxy_request.pk,),
                ),
            )
        else:
            related_requests = (
                VotingProxyRequest.objects.filter(email=voting_proxy_request.email)
                .exclude(
                    status__in=(
                        VotingProxyRequest.STATUS_CREATED,
                        VotingProxyRequest.STATUS_CANCELLED,
                    )
                )
                .values_list("pk", flat=True)
            )
            link = front_url(
                "voting_proxy_request_details",
                query={"vpr": ",".join([str(pk) for pk in related_requests])},
            )
            link = shorten_url(link, secret=True, djan_url_type="M2022")

            return format_html(
                f'<a class="button" href="{link}" target="_blank">➡ Lien vers la page de confirmation</a>'
            )

    matching_buttons.short_description = "Recherche de volontaires"
