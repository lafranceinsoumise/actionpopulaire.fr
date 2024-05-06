from functools import partial
from io import BytesIO

import pandas as pd
import reversion
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from glom import glom, T, Coalesce
from sepaxml.validation import ValidationError

from agir.donations.allocations import (
    create_spending_for_group,
    get_supportgroup_balance,
)
from agir.donations.apps import DonsConfig
from agir.donations.models import SpendingRequest
from agir.donations.spending_requests import get_revision_comment
from agir.donations.tasks import spending_request_notify_group_managers
from agir.gestion.virements import (
    spending_requests_to_bank_transfers,
    generer_fichier_virement,
    BANK_TRANSFER_EMITTER,
)
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


def format_spending_request_attachments(docs):
    if not docs:
        return "-"

    return ", ".join(
        [f"{doc.file.url} ({doc.get_type_display()} : « {doc.title} »)" for doc in docs]
    )


def format_spending_request_for_export(queryset):
    queryset = queryset.with_serializer_prefetch()

    spec = {
        "Identifiant": "id",
        "Titre": "title",
        "Statut": T.get_status_display(),
        "Groupe": "group.name",
        "Dépense de campagne électorale": "campaign",
        "Type de dépense": T.get_timing_display(),
        "Catégorie de demande": T.get_category_display(),
        "Précisions sur le type de demande": "category_precisions",
        "Motif de l'achat": "explanation",
        "Nom du contact": Coalesce("contact_name", "group.contact_phone", default=None),
        "Téléphone": Coalesce("contact_phone", "group.contact_phone", default=None),
        "Événement lié à la dépense": "event",
        "Date de la dépense": "spending_date",
        "Montant de la dépense": "amount",
        "Raison sociale": "bank_account_full_name",
        "IBAN": "bank_account_iban",
        "BIC": "bank_account_bic",
        "RIB": Coalesce("bank_account_rib.url", default=None),
        "Pièce justificatives": (
            "attachments",
            format_spending_request_attachments,
        ),
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
    to_status = SpendingRequest.Status.PAID
    queryset_ids = list(queryset.values_list("id", flat=True))
    queryset.update(status=to_status)

    for spending_request_pk in queryset_ids:
        spending_request_notify_group_managers.delay(
            spending_request_pk, to_status=to_status
        )


mark_spending_request_as_paid.short_description = _(
    "Indiquer ces demandes comme payées"
)
mark_spending_request_as_paid.allowed_permissions = ["change"]
mark_spending_request_as_paid.select_across = True


def save_spending_request_admin_review(
    spending_request, to_status, comment=None, bank_transfer_label=""
):
    with reversion.create_revision(atomic=True):
        from_status = spending_request.status
        if to_status == SpendingRequest.Status.VALIDATED and spending_request:
            available_balance = get_supportgroup_balance(spending_request.group)

            # dans le cas d'une validation, on peut déjà bloquer les fonds s'ils sont suffisants
            if spending_request.amount <= available_balance:
                spending_request.account_operation = create_spending_for_group(
                    group=spending_request.group, amount=spending_request.amount
                )
                to_status = SpendingRequest.Status.TO_PAY

        reversion.set_comment(
            comment
            or get_revision_comment(to_status=to_status, from_status=from_status)
        )
        spending_request.status = to_status
        spending_request.bank_transfer_label = bank_transfer_label
        spending_request.save()

        spending_request_notify_group_managers.delay(
            spending_request.pk,
            to_status=to_status,
            from_status=from_status,
            comment=comment,
        )


def bank_transfers_from_spending_requests_factory(
    name, mark_as_paid=False, emitter="LFI"
):
    def fn(modeladmin, request, queryset):
        error = None
        try:
            virements = spending_requests_to_bank_transfers(queryset)
            data = generer_fichier_virement(
                emetteur=BANK_TRANSFER_EMITTER[emitter],
                virements=virements,
            )
        except ValueError as e:
            error = str(e)
        except ValidationError as e:
            error = (
                (
                    "Le fichier SEPA généré contient des données invalides. Veuillez vérifier les données des demandes "
                    "sélectionnées et ressayer."
                ),
            )

        if error:
            modeladmin.message_user(
                request,
                error,
                level=messages.WARNING,
            )

            return HttpResponseRedirect(request.get_full_path())

        if mark_as_paid:
            mark_spending_request_as_paid(modeladmin, request, queryset)

        filename = f"{emitter}__Virements_{timezone.now().date()}.xml"
        response = HttpResponse(data, content_type="application/xml")
        response["Content-Disposition"] = "attachment; filename=%s" % filename

        return response

    short_description = f"{emitter} : Générer le fichier de virement"
    if mark_as_paid:
        short_description += " et indiquer comme payées"

    fn.short_description = short_description
    fn.allowed_permissions = ["view"]
    fn.select_across = True
    fn.__name__ = name

    return fn


bank_transfers_from_spending_requests = bank_transfers_from_spending_requests_factory(
    "bank_transfers_from_spending_requests_factory",
    mark_as_paid=False,
    emitter="LFI",
)

bank_transfers_from_spending_requests_and_mark_as_paid = (
    bank_transfers_from_spending_requests_factory(
        "bank_transfers_from_spending_requests_and_mark_as_paid",
        mark_as_paid=True,
        emitter="LFI",
    )
)

campaign_bank_transfers_from_spending_requests = (
    bank_transfers_from_spending_requests_factory(
        "campaign_bank_transfers_from_spending_requests",
        mark_as_paid=False,
        emitter="AFCE_LFI_2024",
    )
)

campaign_bank_transfers_from_spending_requests_and_mark_as_paid = (
    bank_transfers_from_spending_requests_factory(
        "campaign_bank_transfers_from_spending_requests_and_mark_as_paid",
        mark_as_paid=True,
        emitter="AFCE_LFI_2024",
    )
)
