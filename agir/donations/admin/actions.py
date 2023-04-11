from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from glom import glom, T, Coalesce

from agir.donations.apps import DonsConfig
from agir.donations.models import SpendingRequest
from agir.payments.models import Payment


def convert_to_donation(
    payment,
    fiscal_resident,
):
    today = timezone.now().date()
    person = payment.person

    assert payment.type != DonsConfig.SINGLE_TIME_DONATION_TYPE
    assert payment.status == Payment.STATUS_COMPLETED

    # seuls les personnes de nationalité françaises, ou résidents fiscaux en France
    # peuvent donner
    assert "nationality" in person.meta
    assert person.meta["nationality"] == "FR" or (
        fiscal_resident and person.location_country == "FR"
    )
    assert person.first_name and person.last_name
    assert person.location_address1 and person.location_zip and person.location_city
    assert person.contact_phone

    payment.meta.update(
        {
            "changes": f"Transformé en don le {today.strftime('%d/%m/%Y')}.",
            "first_name": person.first_name,
            "last_name": person.last_name,
            "location_address1": person.location_address1,
            "location_address2": person.location_address2,
            "location_zip": person.location_zip,
            "location_city": person.location_city,
            "location_country": str(person.location_country),
            "contact_phone": person.contact_phone.as_e164,
            "nationality": person.meta["nationality"],
            "fiscal_resident": fiscal_resident,
        }
    )
    payment.first_name = person.first_name
    payment.last_name = person.last_name
    payment.email = person.email
    payment.type = DonsConfig.SINGLE_TIME_DONATION_TYPE
    payment.save(update_fields=["first_name", "last_name", "email", "type", "meta"])


def format_spending_request_for_export(queryset):
    spec = {
        "Identifiant": "id",
        "Titre": "title",
        "Statut": T.get_status_display(),
        "Groupe": "group.name",
        "Téléphone": Coalesce("group.contact_phone", default=None),
        "Événement lié à la dépense": "event",
        "Catégorie de demande": T.get_category_display(),
        "Précisions sur le type de demande": "category_precisions",
        "Justification de la demande": "explanation",
        "Date de la dépense": "spending_date",
        "Montant de la dépense": "amount",
        "Raison sociale du prestataire": "provider",
        "RIB (format IBAN)": "iban",
        "Nom de la personne qui a payé": "payer_name",
        "Date de création": T.created.astimezone(timezone.get_current_timezone())
        .replace(microsecond=0)
        .isoformat(),
        "Date de modification": T.modified.astimezone(timezone.get_current_timezone())
        .replace(microsecond=0)
        .isoformat(),
    }

    return glom(queryset, [spec])


def export_spending_requests_to_xlsx(modeladmin, request, queryset):
    spending_requests = format_spending_request_for_export(queryset)
    res = pd.DataFrame(spending_requests)
    with BytesIO() as b:
        writer = pd.ExcelWriter(b, engine="xlsxwriter")
        res.to_excel(writer, index=False, sheet_name="Sheet1")
        writer.save()
        filename = f"spending_requests_{timezone.now().date()}.xlsx"
        response = HttpResponse(
            b.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


export_spending_requests_to_xlsx.short_description = f"Exporter les demandes (XLSX)"
export_spending_requests_to_xlsx.allowed_permissions = ["view"]
export_spending_requests_to_xlsx.select_across = True


def export_spending_requests_to_csv(modeladmin, request, queryset):
    spending_requests = format_spending_request_for_export(queryset)
    res = pd.DataFrame(spending_requests)
    filename = f"spending_requests_{timezone.now().date()}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={filename}"
    res.to_csv(path_or_buf=response, index=False)

    return response


export_spending_requests_to_csv.short_description = f"Exporter les demandes (CSV)"
export_spending_requests_to_csv.allowed_permissions = ["view"]
export_spending_requests_to_csv.select_across = True


def mark_spending_request_as_paid(model_admin, request, queryset):
    queryset.update(status=SpendingRequest.STATUS_PAID)


mark_spending_request_as_paid.short_description = _(
    "Indiquer ces demandes comme payées"
)
