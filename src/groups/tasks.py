from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings

from celery import shared_task

from lib.mails import send_mosaico_email

from .models import SupportGroup

# encodes the preferred order when showing the messages
CHANGE_DESCRIPTION = OrderedDict((
    ("information", _("le nom ou la description du groupe")),
    ("location", _("le lieu de rencontre du groupe d'appui")),
    ("contact", _("les informations de contact des référents du groupe"))
))


@shared_task
def send_support_group_changed_notification(support_group_pk, changes):
    group = SupportGroup.objects.get(pk=support_group_pk)

    attendees = group.attendees.all()

    change_descriptions = [desc for label, desc in CHANGE_DESCRIPTION.items() if label in changes]
    change_fragment = render_to_string(
        template_name='lib/list_fragment.html',
        context={'items': change_descriptions}
    )

    # TODO: find adequate way to set up domain names to use for these links
    bindings = {
        "GROUP_CHANGES": change_fragment,
        "GROUP_LINK": "#",
    }

    recipients = [attendee.email for attendee in attendees]

    send_mosaico_email(
        code='',
        subject=_("Les informations de votre groupe d'appui ont été changées"),
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@shared_task
def send_someone_joined_notification(membership_pk):
    pass
