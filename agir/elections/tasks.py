from django.utils.datetime_safe import datetime

from agir.elections.data import get_campaign_manager_for_circonscription_legislative
from agir.elections.models import PollingStationOfficer
from agir.lib.celery import emailing_task
from agir.lib.mailing import send_mosaico_email
from agir.lib.utils import front_url


@emailing_task(post_save=True)
def send_new_polling_station_officer_to_campaign_manager(polling_station_officer_pk):
    polling_station_officer = PollingStationOfficer.objects.get(
        pk=polling_station_officer_pk
    )
    campaign_manager = get_campaign_manager_for_circonscription_legislative(
        polling_station_officer.voting_circonscription_legislative
    )
    if campaign_manager is None:
        return

    bindings = {
        "SALUTATIONS": f"Bonjour {campaign_manager.get('prenom')}",
        "POLLING_STATION_OFFICER_PAGE_URL": front_url(
            "new_polling_station_officer", absolute=True
        ),
        "CODE_CIRCONSCRIPTION": polling_station_officer.voting_circonscription_legislative.code,
        "FIRST_NAME": f"Prénoms : {polling_station_officer.first_name}",
        "LAST_NAME": f"Nom de famille : {polling_station_officer.last_name}",
        "GENDER": f"Genre à l'état civil : {dict(PollingStationOfficer.GENDER_CHOICES)[polling_station_officer.gender]}",
        "BIRTH_DATE": f"Date de naissance : {polling_station_officer.birth_date.strftime('%d/%m/%Y')}",
        "BIRTH_CITY": f"Ville de naissance : {polling_station_officer.birth_city}",
        "BIRTH_COUNTRY": f"Pays de naissance : {polling_station_officer.birth_country.name}",
        "LOCATION_ADDRESS1": f"Adresse : {polling_station_officer.location_address1}",
        "LOCATION_CITY": f"Ville : {polling_station_officer.location_city}",
        "LOCATION_ZIP": f"Code postal : {polling_station_officer.location_zip}",
        "LOCATION_COUNTRY": f"Pays : {polling_station_officer.location_country.name}",
        "VOTING_CIRCONSCRIPTION_LEGISLATIVE": f"Circonscription législative : {polling_station_officer.voting_circonscription_legislative}",
        "POLLING_STATION": f"Bureau de vote : {polling_station_officer.polling_station}",
        "VOTER_ID": f"Numéro national d'électeur : {polling_station_officer.voter_id}",
        "ROLE": f"Rôle : {dict(PollingStationOfficer.ROLE_CHOICES)[polling_station_officer.role]}",
        "HAS_MOBILITY": f"Peut se déplacer dans un autre bureau de vote : {'Oui' if polling_station_officer.has_mobility else 'Non'}",
        "AVAILABLE_VOTING_DATES": f"Dates de disponibilité : {', '.join([datetime.strptime(dt, '%Y-%m-%d').strftime('%d %B') for dt in polling_station_officer.available_voting_dates])}",
        "CONTACT_EMAIL": f"E-mail : {polling_station_officer.contact_email}",
        "CONTACT_PHONE": f"Téléphone : {polling_station_officer.contact_phone}",
    }
    if polling_station_officer.birth_name:
        bindings[
            "BIRTH_NAME"
        ] = f"Nom de naissance : {polling_station_officer.birth_name}"

    if polling_station_officer.location_address2:
        bindings[
            "LOCATION_ADDRESS2"
        ] = f"Complément d'adresse : {polling_station_officer.location_address2}"

    if polling_station_officer.voting_commune:
        bindings[
            "VOTING_LOCATION"
        ] = f"Commune d'inscription : {polling_station_officer.voting_commune.nom_complet}"

    if polling_station_officer.voting_consulate:
        bindings[
            "VOTING_LOCATION"
        ] = f"Consulat d'inscription : {polling_station_officer.voting_consulate.nom}"

    if polling_station_officer.remarks:
        bindings["REMARKS"] = f"Remarques : {polling_station_officer.remarks}"

    subject = f"[Législatives 2022] {polling_station_officer.first_name.upper()} "
    if polling_station_officer.gender == PollingStationOfficer.GENDER_FEMALE:
        subject += (
            "s'est portée volontaire pour être assesseure/déléguée de bureau de vote"
        )
    else:
        subject += (
            "s'est porté volontaire pour être assesseur/délégué de bureau de vote"
        )

    send_mosaico_email(
        code="NEW_POLLING_STATION_OFFICER",
        subject=subject,
        from_email="legislatives@melenchon2022.fr",
        recipients=[campaign_manager.get("email")],
        bindings=bindings,
    )
