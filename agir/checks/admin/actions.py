from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from glom import glom, T, Coalesce


def format_check_payment_for_export(queryset):
    spec = {
        "Identifiant": "id",
        "Type de paiement": T.get_type_display(),
        "Montant": T.get_price_display(),
        "Date de création": T.created.astimezone(timezone.get_current_timezone())
        .replace(microsecond=0)
        .isoformat(),
        "Date de modification": T.modified.astimezone(timezone.get_current_timezone())
        .replace(microsecond=0)
        .isoformat(),
        "Statut": T.get_status_display(),
        "Prénom": "first_name",
        "Nom": "last_name",
        "E-mail": "email",
        "Téléphone": "phone_number",
        "Adresse": "location_address1",
        "Complément d'adresse": "location_address2",
        "Code postal": "location_zip",
        "Ville": "location_city",
        "Pays": "location_country",
        "Meta": "meta",
        "Events": "events",
    }

    return glom(queryset, [spec])


def export_check_payments_to_xlsx(modeladmin, request, queryset):
    check_payments = format_check_payment_for_export(queryset)
    res = pd.DataFrame(check_payments)
    with BytesIO() as b:
        writer = pd.ExcelWriter(b, engine="xlsxwriter")
        res.to_excel(writer, index=False, sheet_name="Sheet1")
        writer.save()
        filename = f"check_payments_{timezone.now().date()}.xlsx"
        response = HttpResponse(
            b.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


export_check_payments_to_xlsx.short_description = f"Exporter les paiements (XLSX)"
export_check_payments_to_xlsx.allowed_permissions = ["view"]
export_check_payments_to_xlsx.select_across = True


def export_check_payments_to_csv(modeladmin, request, queryset):
    check_payments = format_check_payment_for_export(queryset)
    res = pd.DataFrame(check_payments)
    filename = f"check_payments_{timezone.now().date()}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={filename}"
    res.to_csv(path_or_buf=response, index=False)

    return response


export_check_payments_to_csv.short_description = f"Exporter les paiements (CSV)"
export_check_payments_to_csv.allowed_permissions = ["view"]
export_check_payments_to_csv.select_across = True
