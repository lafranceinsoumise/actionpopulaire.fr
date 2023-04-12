from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, ngettext
from rangefilter.filters import DateRangeFilter

from agir.checks.admin import actions, forms, filters
from agir.checks.models import CheckPayment
from agir.lib.admin.panels import AddRelatedLinkMixin
from agir.payments.actions.payments import notify_status_change
from agir.payments.admin import PaymentManagementAdminMixin


@admin.register(CheckPayment)
class CheckPaymentAdmin(
    PaymentManagementAdminMixin, AddRelatedLinkMixin, admin.ModelAdmin
):
    form = forms.CheckPaymentForm
    list_display = (
        "id",
        "person",
        "get_type_display",
        "status",
        "created",
        "modified",
        "get_price_display",
        "email",
        "nom_facturation",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "person_link",
                    "get_type_display",
                    "get_price_display",
                    "created",
                    "status",
                )
            },
        ),
        (
            "Facturation",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "location_country",
                )
            },
        ),
        ("Informations techniques", {"fields": ("meta", "events", "status_buttons")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "price",
                    "type",
                    "mode",
                    "status",
                    "person",
                )
            },
        ),
        (
            "Facturation",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "location_country",
                )
            },
        ),
    )
    readonly_fields = (
        "id",
        "created",
        "person_link",
        "get_type_display",
        "get_price_display",
        "status_buttons",
        "nom_facturation",
    )
    autocomplete_fields = ("person",)
    list_filter = (
        "status",
        ("price", filters.PriceRangeListFilter),
        ("created", admin.DateFieldListFilter),
        ("created", DateRangeFilter),
    )
    search_fields = ("id", "email", "first_name", "last_name")
    actions = (
        actions.export_check_payments_to_csv,
        actions.export_check_payments_to_xlsx,
    )

    def get_fieldsets(self, request, obj=None):
        if obj and obj.id:
            return self.fieldsets

        return self.add_fieldsets

    def has_change_permission(self, request, obj=None):
        """Cette admin ne permet pas la modification"""
        return False

    def nom_facturation(self, obj):
        if obj:
            return f"{obj.first_name} {obj.last_name}"

    def get_urls(self):
        return [
            path(
                "search/",
                self.admin_site.admin_view(self.search_check_view),
                name="checks_checkpayment_search",
            ),
            path(
                "validate/",
                self.admin_site.admin_view(self.validate_check_view),
                name="checks_checkpayment_validate",
            ),
        ] + super().get_urls()

    def search_check_view(self, request):
        if request.method == "POST":
            form = forms.CheckPaymentSearchForm(data=request.POST)

            if form.is_valid():
                return HttpResponseRedirect(
                    "{}?{}".format(
                        reverse("admin:checks_checkpayment_validate"),
                        request.POST.urlencode(),
                    )
                )
        else:
            form = forms.CheckPaymentSearchForm()

        return TemplateResponse(
            request,
            template="admin/checks/checkpayment/search_check.html",
            context={"form": form, "opts": CheckPayment._meta},
        )

    def validate_check_view(self, request):
        get_form = forms.CheckPaymentSearchForm(data=request.GET)
        return_response = HttpResponseRedirect(
            reverse("admin:checks_checkpayment_search")
        )

        if not get_form.is_valid():
            return return_response

        amount, numbers = (
            get_form.cleaned_data["amount"],
            get_form.cleaned_data["numbers"],
        )
        payments = CheckPayment.objects.filter(pk__in=numbers)

        if not len(payments) == len(numbers):
            messages.add_message(
                request,
                messages.ERROR,
                _("Erreur avec un des paiements : veuillez rééssayer"),
            )

        total_price = sum(p.price for p in payments)

        can_validate = (total_price == amount) and all(
            c.status == CheckPayment.STATUS_WAITING for c in payments
        )

        if can_validate and request.method == "POST":
            now = timezone.now().astimezone(timezone.utc).isoformat()

            with transaction.atomic():
                for p in payments:
                    p.status = CheckPayment.STATUS_COMPLETED
                    p.events.append(
                        {
                            "change_status": CheckPayment.STATUS_COMPLETED,
                            "date": now,
                            "origin": "check_payment_admin_validation",
                        }
                    )
                    p.save()

            # notifier en dehors de la transaction, pour être sûr que ça ait été committé
            for p in payments:
                notify_status_change(p)

            messages.add_message(
                request,
                messages.SUCCESS,
                ngettext(
                    "Chèque %(numbers)s validé",
                    "Chèques %(numbers)s validés",
                    len(numbers),
                )
                % {"numbers": ", ".join(str(n) for n in numbers)},
            )
            return return_response

        return TemplateResponse(
            request,
            "admin/checks/checkpayment/validate_check.html",
            context={
                "checks": payments,
                "can_validate": can_validate,
                "total_price": total_price,
                "check_amount": amount,
                "opts": CheckPayment._meta,
            },
        )
