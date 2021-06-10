from rest_framework import serializers
from django.template.defaultfilters import date as _date

from agir.activity.models import Activity
from agir.lib.serializers import FlexibleFieldsMixin
from agir.lib.utils import front_url
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment

__all__ = ["ACTIVITY_NOTIFICATION_SERIALIZERS"]

CHANGED_DATA_LABEL = {
    "name": "le nom",
    "description": "le détail",
    "start_time": "l'horaire",
    "end_time": "l'horaire",
    "contact_name": "le contact",
    "contact_email": "le contact",
    "contact_phone": "le contact",
    "location_name": "le lieu",
    "location_address1": "le lieu",
    "location_address2": "le lieu",
    "location_city": "le lieu",
    "location_zip": "le lieu",
    "location_country": "le lieu",
    "facebook": "le lien facebook",
}


def activity_notification_url(
    *args, activity=None, **kwargs,
):
    if activity is not None:
        query = kwargs.get("query", {})
        query["from_activity"] = str(activity.pk)
        kwargs.update({"query": query})
    return front_url(*args, **kwargs)


class ActivityNotificationSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(read_only=True)
    tag = serializers.CharField(read_only=True, source="type")
    title = serializers.ReadOnlyField(default="Action Populaire")
    body = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    icon = serializers.ReadOnlyField(default=None)
    timestamp = serializers.DateTimeField(read_only=True)
    status = serializers.CharField()

    def get_body(self, activity):
        return ""

    def get_url(self, activity):
        return activity_notification_url("list_activities", activity=activity)

    class Meta:
        model = Activity
        fields = [
            "id",
            "type",
            "tag",
            "title",
            "body",
            "url",
            "icon",
            "timestamp",
            "status",
        ]


class GroupInvitationActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.ReadOnlyField(default="Nouvelle invitation")

    def get_body(self, activity):
        return (
            f"Vous avez été invité-e à rejoindre le groupe {activity.supportgroup.name}"
        )

    def get_url(self, activity):
        return activity_notification_url(
            "view_group", activity=activity, kwargs={"pk": activity.supportgroup_id}
        )


class NewMemberActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.ReadOnlyField(default="Nouveau membre dans votre groupe ! 😀")

    def get_body(self, activity):
        return (
            f"{activity.individual.display_name} a rejoint {activity.supportgroup.name}"
        )

    def get_url(self, activity):
        return activity_notification_url(
            "view_group_settings_members",
            activity=activity,
            kwargs={"pk": activity.supportgroup_id},
        )


class WaitingLocationGroupActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    def get_body(self, activity):
        return f"Précisez la localisation de {activity.supportgroup.name}"

    def get_url(self, activity):
        return activity_notification_url(
            "view_group_settings_location",
            activity=activity,
            kwargs={"pk": activity.supportgroup_id},
        )


class WaitingLocationEventActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    def get_body(self, activity):
        return f"Précisez la localisation de {activity.event.name}"

    def get_url(self, activity):
        return activity_notification_url(
            "view_group_settings_location",
            activity=activity,
            kwargs={"pk": activity.event_id},
        )


class GroupMembershipLimitReminderActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    title = serializers.SerializerMethodField()

    def get_title(self, activity):
        membership_limit_notification_step = activity.meta[
            "membershipLimitNotificationStep"
        ]
        if membership_limit_notification_step > 3:
            return "Action requise pour votre groupe"
        return "Action Populaire"

    def get_body(self, activity):
        membership_count = activity.meta["membershipCount"]
        membership_limit_notification_step = activity.meta[
            "membershipLimitNotificationStep"
        ]
        if membership_limit_notification_step == 0:
            return f"Vous êtes maintenant {membership_count} dans votre équipe ! Vous avez atteint le nombre idéal de personnes"

        if (
            membership_limit_notification_step == 1
            or membership_limit_notification_step == 2
        ):
            return f"Votre groupe a atteint les {membership_count} personnes ! Afin que chacun·e puisse s'impliquer et pour permettre une plus grande répartition de l'action, nous vous invitons à diviser votre équipe"

        if membership_limit_notification_step == 3:
            return f"Votre équipe est trop nombreuse {activity.supportgroup.name} compte plus de {membership_count - 1} personnes ! Il est temps de vous diviser en plusieurs équipes pour permettre une plus grande répartition de l’action"

        return "Votre équipe a trop de membres. Divisez-la pour renforcer le réseau d'action"

    def get_url(self, activity):
        return activity_notification_url(
            "view_group_settings_members",
            activity=activity,
            kwargs={"pk": activity.supportgroup_id},
        )


class GroupInfoUpdateActivityNotificationSerializer(ActivityNotificationSerializer):
    def get_body(self, activity):
        changed_data = activity.meta["changed_data"]
        if isinstance(changed_data, list) and len(changed_data) > 0:
            changed_data = set(
                [
                    CHANGED_DATA_LABEL[field]
                    for field in changed_data
                    if field in CHANGED_DATA_LABEL
                ]
            )
            if len(changed_data) == 1:
                return f"{changed_data.pop().capitalize()} de {activity.supportgroup.name} a été mis à jour"
            return f"{', '.join(changed_data).capitalize()} de {activity.supportgroup.name} ont été mis à jour"
        return f"{activity.supportgroup.name} a été mis à jour"

    def get_url(self, activity):
        return activity_notification_url(
            "view_group", activity=activity, kwargs={"pk": activity.supportgroup_id}
        )


class AcceptedInvitationMemberActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    title = serializers.ReadOnlyField(default="Invitation acceptée ✨")

    def get_body(self, activity):
        return f"{activity.individual.display_name} a rejoint {activity.supportgroup.name} en acceptant une invitation"

    def get_url(self, activity):
        return activity_notification_url(
            "view_group_settings_members",
            activity=activity,
            kwargs={"pk": activity.supportgroup_id},
        )


class NewAttendeeActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.ReadOnlyField(default="Nouveau participant 👍")

    def get_body(self, activity):
        return (
            f"{activity.individual.display_name} participera à {activity.event.name} !"
        )

    def get_url(self, activity):
        return activity_notification_url(
            "manage_event", activity=activity, kwargs={"pk": activity.event_id},
        )


class EventUpdateActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, activity):
        return f"{activity.event.name} : mise à jour"

    def get_body(self, activity):
        changed_data = activity.meta["changed_data"]
        if isinstance(changed_data, list) and len(changed_data) > 0:
            changed_data = set(
                [
                    CHANGED_DATA_LABEL[field]
                    for field in changed_data
                    if field in CHANGED_DATA_LABEL
                ]
            )
            if len(changed_data) == 1:
                return f"{changed_data.pop().capitalize()} de {activity.event.name} a été mis à jour"
            return f"{', '.join(changed_data).capitalize()} de {activity.event.name} ont été mis à jour"
        return f"{activity.event.name} a été mis à jour"

    def get_url(self, activity):
        return activity_notification_url(
            "view_event", activity=activity, kwargs={"pk": activity.event_id}
        )


class NewEventMyGroupsActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, activity):
        return f"📆 {activity.event.name}, {activity.event.start_time.strftime('%d/%m')} à {activity.event.start_time.strftime('%H:%M')}"

    def get_body(self, activity):
        return f"Nouvel événement de {activity.supportgroup.name} — Confirmez votre participation pour recevoir les mises à jour"

    def get_url(self, activity):
        return activity_notification_url(
            "view_event", activity=activity, kwargs={"pk": activity.event_id},
        )


class NewReportActivityNotificationSerializer(ActivityNotificationSerializer):
    def get_body(self, activity):
        return f"Le compte-rendu de {activity.event.name} du {activity.event.start_time.strftime('%d/%m')} a été ajouté"

    def get_url(self, activity):
        return activity_notification_url(
            "view_event", activity=activity, kwargs={"pk": activity.event_id},
        )


class CancelledEventActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.ReadOnlyField(default="Annulation d'événement")

    def get_body(self, activity):
        return f"{activity.event.name} a été annulé"


class ReferralActivityNotificationSerializer(ActivityNotificationSerializer):
    def get_body(self, activity):
        return f"Grâce à vous, {activity.individual.display_name} a parrainé la candidature de Jean-Luc Mélenchon"


class GroupCoorganizationAcceptedActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    title = serializers.ReadOnlyField(default="Invitation acceptée ✨")

    def get_body(self, activity):
        return f"{activity.supportgroup.name} a accepté de co-organiser {activity.event.name}"

    def get_url(self, activity):
        return activity_notification_url(
            "manage_event", activity=activity, kwargs={"pk": activity.event_id},
        )


class NewMembersThroughTransferActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    title = serializers.ReadOnlyField(default="Transfert de membres")

    def get_body(self, activity):
        if activity.meta["transferredMemberships"] > 1:
            return f"{activity.meta['transferredMemberships']} membres ont rejoint {activity.supportgroup.name} suite à un transfert depuis {activity.meta['oldGroup']}."
        return f"Un membre a rejoint {activity.supportgroup.name} suite à un transfert depuis {activity.meta['oldGroup']}"

    def get_url(self, activity):
        return activity_notification_url(
            "view_group_settings_members",
            activity=activity,
            kwargs={"pk": activity.supportgroup_id},
        )


class TransferredGroupMemberActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    title = serializers.ReadOnlyField(
        default="Vous avez été transféré·e vers un nouveau groupe"
    )

    def get_body(self, activity):
        return f"Vous avez été transféré·e de {activity.meta['oldGroup']} et avez rejoint {activity.supportgroup.name}. Votre nouvelle équipe vous attend !"

    def get_url(self, activity):
        return activity_notification_url(
            "view_group", activity=activity, kwargs={"pk": activity.supportgroup_id},
        )


class WaitingPaymentActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.ReadOnlyField(default="Paiement en attente")

    def get_body(self, activity):
        return f"Vous n'avez pas encore réglé votre place pour l'événément : {activity.event.name}"

    def get_url(self, activity):
        # TODO: replace with payment url once the activity is actually implemented
        return activity_notification_url(
            "view_event", activity=activity, kwargs={"pk": activity.event_id},
        )


class GroupCoorganizationInviteActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    title = serializers.ReadOnlyField(default="Invitation en attente")

    def get_body(self, activity):
        return f"Votre groupe {activity.supportgroup.name} est invité à co-organiser {activity.event.name}"

    def get_url(self, activity):
        return activity_notification_url(
            "view_event", activity=activity, kwargs={"pk": activity.event_id},
        )


class GroupCoorganizationInfoActivityNotificationSerializer(
    ActivityNotificationSerializer
):
    title = serializers.ReadOnlyField(default="📆 Nouvel événement co-organisé")

    def get_body(self, activity):
        return f"Votre groupe sera présent à {activity.event.name}"

    def get_url(self, activity):
        return activity_notification_url(
            "view_event", activity=activity, kwargs={"pk": activity.event_id},
        )


class NewMessageActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.SerializerMethodField()
    icon = serializers.ImageField(source="individual.image")

    def get_title(self, activity):
        return activity.individual.display_name

    def get_body(self, activity):
        try:
            message = SupportGroupMessage.objects.get(pk=activity.meta["message"])
            return message.text
        except:
            return f"Un nouveau message a été publié dans le groupe {activity.supportgroup.name}"

    def get_url(self, activity):
        return activity_notification_url(
            "user_message_details",
            activity=activity,
            kwargs={"pk": activity.meta["message"],},
        )


class NewCommentActivityNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.SerializerMethodField()
    icon = serializers.ImageField(source="individual.image")

    def get_title(self, activity):
        return f"{activity.individual.display_name} a commenté"

    def get_body(self, activity):
        try:
            message = SupportGroupMessageComment.objects.get(
                pk=activity.meta["comment"]
            )
            return message.text
        except:
            return f"Un nouveau commentaire a été publié dans le groupe {activity.supportgroup.name}"

    def get_url(self, activity):
        return activity_notification_url(
            "user_message_details",
            activity=activity,
            kwargs={"pk": activity.meta["message"],},
        )


class EventSuggestionNotificationSerializer(ActivityNotificationSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, activity):
        return f"📆 Ce {_date(activity.event.start_time, 'l')} : passez à l'action !"

    def get_body(self, activity):
        return f"{activity.event.name}"

    def get_url(self, activity):
        return activity_notification_url(
            "view_event", activity=activity, kwargs={"pk": activity.event_id}
        )


ACTIVITY_NOTIFICATION_SERIALIZERS = {
    Activity.TYPE_GROUP_INVITATION: GroupInvitationActivityNotificationSerializer,
    Activity.TYPE_NEW_MEMBER: NewMemberActivityNotificationSerializer,
    Activity.TYPE_WAITING_LOCATION_GROUP: WaitingLocationGroupActivityNotificationSerializer,
    Activity.TYPE_WAITING_LOCATION_EVENT: WaitingLocationEventActivityNotificationSerializer,
    Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER: GroupMembershipLimitReminderActivityNotificationSerializer,
    Activity.TYPE_GROUP_INFO_UPDATE: GroupInfoUpdateActivityNotificationSerializer,
    Activity.TYPE_ACCEPTED_INVITATION_MEMBER: AcceptedInvitationMemberActivityNotificationSerializer,
    Activity.TYPE_NEW_ATTENDEE: NewAttendeeActivityNotificationSerializer,
    Activity.TYPE_EVENT_UPDATE: EventUpdateActivityNotificationSerializer,
    Activity.TYPE_NEW_EVENT_MYGROUPS: NewEventMyGroupsActivityNotificationSerializer,
    Activity.TYPE_NEW_REPORT: NewReportActivityNotificationSerializer,
    Activity.TYPE_CANCELLED_EVENT: CancelledEventActivityNotificationSerializer,
    Activity.TYPE_REFERRAL: ReferralActivityNotificationSerializer,
    Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED: GroupCoorganizationAcceptedActivityNotificationSerializer,
    Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER: NewMembersThroughTransferActivityNotificationSerializer,
    Activity.TYPE_TRANSFERRED_GROUP_MEMBER: TransferredGroupMemberActivityNotificationSerializer,
    Activity.TYPE_WAITING_PAYMENT: WaitingPaymentActivityNotificationSerializer,
    Activity.TYPE_GROUP_COORGANIZATION_INVITE: GroupCoorganizationInviteActivityNotificationSerializer,
    Activity.TYPE_GROUP_COORGANIZATION_INFO: GroupCoorganizationInfoActivityNotificationSerializer,
    Activity.TYPE_NEW_MESSAGE: NewMessageActivityNotificationSerializer,
    Activity.TYPE_NEW_COMMENT: NewCommentActivityNotificationSerializer,
    Activity.TYPE_EVENT_SUGGESTION: EventSuggestionNotificationSerializer,
}
