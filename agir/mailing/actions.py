import json

from django.db import transaction
from django.utils.html import escapejs, escape
from nuntius.models import Campaign


def _deep_replace(dictionary: dict, search, replace):
    # deeply replace values in a dict where all values are str or dict of str
    new_dict = {}

    for key in dictionary:
        if isinstance(dictionary[key], str):
            new_dict[key] = dictionary[key].replace(search, replace)
        elif isinstance(dictionary[key], dict):
            new_dict[key] = _deep_replace(dictionary[key], search, replace)
        elif isinstance(dictionary[key], list):
            new_dict[key] = [
                _deep_replace(item, search, replace) for item in dictionary[key]
            ]
        else:
            new_dict[key] = dictionary[key]

    return new_dict


UPDATABLE_CAMPAIGN_KEYS = [
    "message_subject",
    "from_email",
    "from_name",
    "reply_to_email",
    "reply_to_name",
    "message_subject",
    "utm_name",
    "start_date",
    "end_date",
]


def update_campaign_from_data(campaign: Campaign, data):
    for key in data.keys():
        if not key.startswith("campaign_"):
            continue
        value = data.get(key)
        campaign_key = key.replace("campaign_", "")
        if hasattr(campaign, campaign_key) and campaign_key in UPDATABLE_CAMPAIGN_KEYS:
            setattr(campaign, campaign_key, value)

    for field in data:
        substitute = escape(str(data[field]).replace("{", ""))

        campaign.message_mosaico_data = json.dumps(
            _deep_replace(
                json.loads(campaign.message_mosaico_data), f"[{field}]", substitute
            )
        )
        campaign.message_content_html = campaign.message_content_html.replace(
            f"[{field}]", substitute
        )
        campaign.message_content_text = campaign.message_content_text.replace(
            f"[{field}]", substitute
        )
        campaign.save()

    return campaign


def create_campaign_from_submission(data, person, campaign: Campaign):
    with transaction.atomic():
        campaign.pk = None
        campaign.name = campaign.name + f" (copie par {str(person)})"
        campaign = update_campaign_from_data(campaign, data)
        campaign.save()
        return campaign


def create_or_reset_campaign_from_data(template: Campaign, data, campaign_id=None):
    campaign = template

    with transaction.atomic():
        create = campaign_id is None
        if create:
            campaign.pk = None
        else:
            campaign.pk = campaign_id

        campaign.name = data.get("campaign_name", campaign.name + f" (copie)")
        campaign = update_campaign_from_data(campaign, data)
        campaign.save()

        return campaign, create
