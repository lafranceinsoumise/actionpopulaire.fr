from django.contrib import admin
from django.contrib.admin import TabularInline
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter
from agir.lib.utils import front_url, shorten_url
from agir.voting_proxies.actions import cancel_voting_proxy_requests
from agir.voting_proxies.admin.actions import (
    fulfill_voting_proxy_requests,
    export_voting_proxies,
    export_voting_proxy_requests,
)
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest


class CommuneListFilter(AutocompleteRelatedModelFilter):
    field_name = "commune"
    title = "commune"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(commune=self.value()) | Q(commune__commune_parent=self.value())
            )

        return queryset


class ConsulateListFilter(AutocompleteRelatedModelFilter):
    field_name = "consulate"
    title = "consulat"


class DepartementListFilter(AutocompleteRelatedModelFilter):
    field_name = "commune__departement"
    title = "département"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(commune__departement=self.value())
                | Q(commune__commune_parent__departement=self.value())
            )

        return queryset


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
                ).values_list("pk", flat=True)
            )
        if self.value() == "1":
            return queryset.filter(
                status__in=(VotingProxy.STATUS_CREATED, VotingProxy.STATUS_AVAILABLE),
            )

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
        DepartementListFilter,
        ConsulateListFilter,
    )
    autocomplete_fields = ("commune", "consulate")
    readonly_fields = ("created", "polling_station_label")

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

    def polling_station_label(self, instance):
        return instance.polling_station_label

    polling_station_label.short_description = "Libellé du bureau de vote"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("commune", "consulate")

    def has_export_permission(self, request):
        return request.user.has_perm("people.export_people")

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
    readonly_fields = (
        *VoterModelAdmin.readonly_fields,
        "address",
        "last_matched",
        "accepted_request_page_link",
    )
    autocomplete_fields = (
        *VoterModelAdmin.autocomplete_fields,
        "person",
    )

    actions = (export_voting_proxies,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("person")
            .prefetch_related("voting_proxy_requests")
        )

    def person_link(self, voting_proxy):
        if voting_proxy.person is None:
            return "-"
        href = reverse("admin:people_person_change", args=(voting_proxy.person_id,))
        return mark_safe(format_html(f'<a href="{href}">{voting_proxy.person}</a>'))

    person_link.short_description = "personne"

    def address(self, voting_proxy):
        if voting_proxy.person is None:
            return "-"

        href = reverse("admin:people_person_change", args=(voting_proxy.person_id,))

        return mark_safe(
            format_html(
                f'<a target="_blank" href="{href}#id_location_address1">{voting_proxy.person.short_address}</a>'
            )
        )

    address.short_description = "Adresse"

    def confirmed_dates(self, voting_proxy):
        return [
            request.voting_date
            for request in voting_proxy.voting_proxy_requests.exclude(
                status=VotingProxyRequest.STATUS_CANCELLED
            ).only("voting_date")
        ]

    confirmed_dates.short_description = "dates acceptées"

    def accepted_request_page_link(self, voting_proxy):
        accepted_requests = voting_proxy.voting_proxy_requests.filter(
            status__in=(
                VotingProxyRequest.STATUS_ACCEPTED,
                VotingProxyRequest.STATUS_CONFIRMED,
            )
        )

        if len(accepted_requests) == 0:
            return "-"

        link = front_url(
            "accepted_voting_proxy_requests", kwargs={"pk": voting_proxy.pk}
        )
        link = shorten_url(link, secret=True)

        return format_html(
            f'<a class="button" href="{link}" target="_blank">'
            f"  ➡ Lien vers la page des demandes acceptées"
            f"</a>"
        )

    accepted_request_page_link.short_description = "Demandes acceptées"


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
    readonly_fields = (
        *VoterModelAdmin.readonly_fields,
        "matching_buttons",
        "cancel_button",
    )
    autocomplete_fields = (
        *VoterModelAdmin.autocomplete_fields,
        "proxy",
    )
    actions = (export_voting_proxy_requests,)

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

    def cancel_voting_proxy_request_view(self, request, pk):
        voting_proxy_request = VotingProxyRequest.objects.filter(pk=pk)
        cancel_voting_proxy_requests(voting_proxy_request)
        return HttpResponseRedirect(
            reverse(
                "admin:voting_proxies_votingproxyrequest_change",
                args=(pk,),
            ),
        )

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
                "<uuid:pk>/cancel/",
                self.admin_site.admin_view(self.cancel_voting_proxy_request_view),
                name="votingproxies_votingproxyrequest_cancel_voting_proxy_request",
            ),
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

        if voting_proxy_request.status == VotingProxyRequest.STATUS_CREATED:
            return format_html(
                '<p><a href="{match_voting_proxy_request}" class="button">'
                "  Chercher uniquement pour cette demande"
                "</a></p>"
                '<p style="margin-top: 4px;"><a href="{match_person_voting_proxy_requests}" class="button">'
                "  Chercher pour toutes les demandes de cette personne"
                "</a></p>"
                '<p style="margin-top: 4px;"><a href="{reply_to_url}" class="button">'
                "  Lien d'acceptation de la demande"
                "</a></p>",
                match_voting_proxy_request=reverse(
                    "admin:votingproxies_votingproxyrequest_match_voting_proxy_request",
                    args=(voting_proxy_request.pk,),
                ),
                match_person_voting_proxy_requests=reverse(
                    "admin:votingproxies_votingproxyrequest_match_person_voting_proxy_requests",
                    args=(voting_proxy_request.pk,),
                ),
                reply_to_url=voting_proxy_request.reply_to_url,
            )

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
        link = shorten_url(link, secret=True)

        return format_html(
            f'<a class="button" href="{link}" target="_blank">➡ Lien vers la page de confirmation</a>'
        )

    matching_buttons.short_description = "Recherche de volontaires"

    def cancel_button(self, voting_proxy_request):
        if voting_proxy_request.status == VotingProxyRequest.STATUS_CANCELLED:
            return "-"

        return format_html(
            '<a href="{cancel_voting_proxy_request}" class="button">'
            "  Annuler cette demande"
            "</a>"
            "<div style='margin: 0; padding-left: 0;' class='help'>"
            "  Le·la volontaire sera prévenu·e par e-mail de l'annulation"
            "</div>",
            cancel_voting_proxy_request=reverse(
                "admin:votingproxies_votingproxyrequest_cancel_voting_proxy_request",
                args=(voting_proxy_request.pk,),
            ),
        )

    cancel_button.short_description = "Annulation"
