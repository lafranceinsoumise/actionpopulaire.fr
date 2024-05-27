import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from slugify import slugify

SFR_CSV_HEADERS = [
    "NAME",
    "FORENAME",
    "PHONENUMBER1",
    "COUNTRYCODE1",
    "PHONENUMBER2",
    "COUNTRYCODE2",
    "PHONENUMBER3",
    "COUNTRYCODE3",
    "PHONENUMBER4",
    "COUNTRYCODE4",
    "PHONENUMBER5",
    "COUNTRYCODE5",
    "PHONENUMBER6",
    "COUNTRYCODE6",
    "FAXNUMBER",
    "FAXCOUNTRYCODE",
    "EMAIL1",
    "EXTERNALREFERENCE",
    "INFO1",
    "INFO2",
    "INFO3",
    "INFO4",
]


def download_segment_as_csv_for_sms(segment):
    people = (
        segment.get_people()
        .exclude(contact_phone__exact="")
        .filter(subscribed_sms=True)
        .only("last_name", "first_name", "contact_phone", "pk")
    )
    people = [
        {
            "NAME": p.last_name.title(),
            "FORENAME": p.first_name.title(),
            "PHONENUMBER1": f"0{p.contact_phone.as_e164[3:]}",
            "EXTERNALREFERENCE": str(p.pk),
        }
        for p in people
    ]

    people = (
        pd.concat([pd.DataFrame(columns=SFR_CSV_HEADERS), pd.DataFrame(people)])
        .dropna(subset=["PHONENUMBER1"])
        .fillna("")
    )

    response = HttpResponse(content_type="text/csv")
    filename = (
        f"SMS{segment.id}_{slugify(segment.name)}_{timezone.now().strftime('%Y-%m-%d')}"
    )
    response["Content-Disposition"] = f"attachment; filename={filename}"
    people.to_csv(path_or_buf=response, index=False)

    return response
