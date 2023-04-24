from django.db import transaction

from agir.events.serializers import EventEmailCampaignSerializer
from agir.mailing.actions import create_or_reset_campaign_from_data


class EventGenerateMailingCampaignError(Exception):
    pass


def generate_mailing_campaign(event):
    if event.subtype.campaign_template is None:
        raise EventGenerateMailingCampaignError(
            "Aucun modèle de campagne e-mail n'a été défini pour ce sous-type d'événement"
        )

    template = event.subtype.campaign_template
    data = EventEmailCampaignSerializer(event).data

    with transaction.atomic():
        campaign, created = create_or_reset_campaign_from_data(
            template, data, event.email_campaign_id
        )
        event.email_campaign = campaign
        event.save()

        return campaign, created
