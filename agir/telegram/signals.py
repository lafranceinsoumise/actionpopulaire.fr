from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from pyrogram import ChatPermissions, InputPhoneContact

from agir.lib.phone_numbers import is_mobile_number
from agir.telegram.models import TelegramGroup


@receiver(pre_save, sender=TelegramGroup, dispatch_uid="create_group_if_not_exists")
def create_group(sender, instance, **kwargs):
    with instance.admin_session.create_client() as client:
        if instance.telegram_id is None:
            instance.telegram_id = client.create_supergroup(title=instance.name).id
            if instance.type == TelegramGroup.CHAT_TYPE_SUPERGROUP:
                client.set_chat_permissions(
                    instance.telegram_id,
                    ChatPermissions(
                        can_send_messages=False,
                        can_change_info=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                    ),
                )


@receiver(post_save, sender=TelegramGroup, dispatch_uid="update_members")
def update_members(sender, instance, **kwargs):
    with instance.admin_session.create_client() as client:
        client.add_contacts(
            [
                InputPhoneContact(
                    phone=str(person.contact_phone),
                    first_name=person.first_name,
                    last_name=person.last_name,
                )
                for person in instance.segment.get_subscribers_queryset()
                if person.contact_phone and is_mobile_number(person.contact_phone)
            ]
        )
        client.add_chat_members(
            instance.telegram_id,
            [
                str(person.contact_phone)
                for person in instance.segment.get_subscribers_queryset()
                if person.contact_phone and is_mobile_number(person.contact_phone)
            ],
        )
