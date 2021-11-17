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


def create_campaign_from_submission(submission, campaign: Campaign):
    with transaction.atomic():
        campaign.pk = None
        campaign.name = campaign.name + f" (copie par {str(submission.person)})"
        campaign.message_from_email = submission.data.get(
            "campaign_from_email", campaign.message_from_email
        )
        campaign.message_from_name = submission.data.get(
            "campaign_from_name", campaign.message_from_name
        )
        campaign.message_reply_to_email = submission.data.get(
            "campaign_reply_to_email", campaign.message_reply_to_email
        )
        campaign.message_reply_to_name = submission.data.get(
            "campaign_reply_to_name", campaign.message_reply_to_name
        )

        for field in submission.data:
            substitute = escape(str(submission.data[field]).replace("{", ""))

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
