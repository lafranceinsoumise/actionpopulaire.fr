from agir.lib.celery import emailing_task
from agir.lib.mailing import send_template_email
from agir.polls.models import PollChoice


@emailing_task()
def send_vote_confirmation_email(poll_choice_id):
    try:
        poll_choice = PollChoice.objects.select_related("poll", "person").get(
            id=poll_choice_id
        )
    except PollChoice.DoesNotExist:
        return

    send_template_email(
        "polls/confirmation_email",
        recipients=[poll_choice.person],
        bindings={"poll_choice": poll_choice, "poll": poll_choice.poll},
    )
