from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext, ngettext

from agir.donations.form_fields import MoneyField
from agir.lib.admin.panels import AddRelatedLinkMixin
from agir.payments.actions.payments import notify_status_change
from agir.payments.admin import PaymentManagementAdminMixin
from .models import CheckPayment


class CheckPaymentSearchForm(forms.Form):
    numbers = forms.CharField(
        label="Numéro(s) de chèque",
        required=True,
        help_text=_(
            "Saisissez les numéros de transaction du chèque, séparés par des espaces"
        ),
    )
    amount = MoneyField(label="Montant du chèque", min_value=0, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Rechercher"))

    def clean_numbers(self):
        numbers = self.cleaned_data["numbers"].split()

        try:
            numbers = [int(n) for n in numbers]
        except ValueError:
            raise forms.ValidationError(
                _("Entrez les numéros de chèque séparés par des espace")
            )

        missing_checks = []
        for n in numbers:
            try:
                CheckPayment.objects.get(pk=n)
            except CheckPayment.DoesNotExist:
                missing_checks.append(n)

        if len(missing_checks) == 1:
            raise forms.ValidationError(
                gettext("Le chèque n°{n} n'existe pas.").format(n=missing_checks[0])
            )
        elif missing_checks:
            raise forms.ValidationError(
                gettext("Les paiements de numéros {numeros} n'existent pas.").format(
                    numeros=", ".join([str(i) for i in missing_checks])
                )
            )

        return numbers


@admin.register(CheckPayment)
class CheckPaymentAdmin(
    PaymentManagementAdminMixin, AddRelatedLinkMixin, admin.ModelAdmin
):
    list_display = (
        "id",
        "person",
        "get_type_display",
        "status",
        "created",
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

    readonly_fields = (
        "person_link",
        "get_type_display",
        "get_price_display",
        "status_buttons",
        "nom_facturation",
    )

    list_filter = ("price", "status")
    search_fields = ("id", "email", "first_name", "last_name")

    def has_add_permission(self, request):
        """Forbidden to add checkpayment through this model admin"""
        return False

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
            form = CheckPaymentSearchForm(data=request.POST)

            if form.is_valid():
                return HttpResponseRedirect(
                    "{}?{}".format(
                        reverse("admin:checks_checkpayment_validate"),
                        request.POST.urlencode(),
                    )
                )
        else:
            form = CheckPaymentSearchForm()

        return TemplateResponse(
            request,
            template="admin/checks/checkpayment/search_check.html",
            context={"form": form, "opts": CheckPayment._meta},
        )

    def validate_check_view(self, request):
        get_form = CheckPaymentSearchForm(data=request.GET)
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
