from agir.event_requests.models import EventSpeaker
from agir.lib.celery import emailing_task
from agir.lib.mailing import send_template_email
from agir.lib.utils import front_url


@emailing_task()
def send_new_event_speaker_request_notification(speaker_pk):
    speaker = (
        EventSpeaker.objects.select_related("person")
        .with_serializer_prefetch()
        .filter(pk=speaker_pk)
        .first()
    )

    if speaker is None:
        return

    send_template_email(
        template_name="event_speaker/new_event_speaker_request_email.html",
        bindings={
            "event_speaker_page_url": front_url("event_speaker", absolute=True),
            "event_speaker_themes": [
                f"{theme} ({theme.event_theme_type})"
                for theme in speaker.event_themes.all().order_by("event_theme_type_id")
            ],
        },
        recipients=[speaker.person],
    )
