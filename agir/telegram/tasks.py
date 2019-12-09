from time import sleep

from celery import shared_task
from django.db import transaction
from pyrogram import ChatPermissions, InputPhoneContact
from pyrogram.errors import PeerIdInvalid

from agir.lib.phone_numbers import is_mobile_number
from agir.telegram.models import TelegramGroup


@shared_task(max_retries=2, bind=True)
def update_telegram_groups(self, pk):
    with transaction.atomic():
        try:
            instance = TelegramGroup.objects.select_for_update().get(pk=pk)
        except TelegramGroup.DoesNotExist:
            return

        with instance.admin_session.create_client() as client:
            current_members = set(
                member.user.phone_number
                for chat_id in instance.telegram_ids
                for member in client.iter_chat_members(chat_id)
            )
            chat_empty_slots = {
                chat_id: 200 - client.get_chat_members_count(chat_id)
                for chat_id in instance.telegram_ids
            }

            new_members = [
                person
                for person in instance.segment.get_subscribers_queryset()
                if person.contact_phone
                and is_mobile_number(person.contact_phone)
                and str(person.contact_phone) not in current_members
            ]

            missing_slots = len(new_members) - sum(chat_empty_slots.values())

            while missing_slots > 0:
                title = f"{instance.name} {len(instance.telegram_ids) + 1}"
                if instance.type == TelegramGroup.CHAT_TYPE_SUPERGROUP:
                    chat_id = client.create_supergroup(title=title).id
                    client.set_chat_permissions(
                        chat_id,
                        ChatPermissions(
                            can_send_messages=False,
                            can_change_info=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                        ),
                    )
                elif instance.type == TelegramGroup.CHAT_TYPE_CHANNEL:
                    chat_id = client.create_channel(title=title).id
                instance.telegram_ids = instance.telegram_ids + [chat_id]
                chat_empty_slots[chat_id] = 200
                missing_slots = missing_slots - 200
                if missing_slots > 0:
                    sleep(5)

            client.add_contacts(
                [
                    InputPhoneContact(
                        phone=str(person.contact_phone),
                        first_name=person.first_name,
                        last_name=person.last_name,
                    )
                    for person in new_members
                ]
            )

            new_members_iterator = iter(new_members)

            for chat_id in instance.telegram_ids:
                chat_new_members = list()

                while len(chat_new_members) <= chat_empty_slots[chat_id]:
                    try:
                        phone_number = str(next(new_members_iterator).contact_phone)
                        client.resolve_peer(phone_number)
                    except PeerIdInvalid:
                        continue
                    except StopIteration:
                        break
                    else:
                        chat_new_members.append(phone_number)

                client.add_chat_members(chat_id, chat_new_members)
                sleep(5)

        TelegramGroup.objects.filter(pk=pk).update(telegram_ids=instance.telegram_ids)
