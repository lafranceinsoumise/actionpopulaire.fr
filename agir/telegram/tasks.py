from time import sleep

from celery import shared_task
from django.db import transaction
from pyrogram.types import ChatPermissions, InputPhoneContact
from pyrogram.errors import PeerIdInvalid

from agir.lib.phone_numbers import is_mobile_number
from agir.telegram.models import TelegramGroup, TELEGRAM_META_KEY

DEFAULT_GROUP_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
)


def is_telegram_user(client, person):
    try:
        client.resolve_peer(str(person.contact_phone))

        if not person.meta.get(TELEGRAM_META_KEY, False):
            person.meta[TELEGRAM_META_KEY] = True
            person.save(update_fields=("meta",))

        return True

    except PeerIdInvalid:
        if person.meta.get(TELEGRAM_META_KEY, True):
            person.meta[TELEGRAM_META_KEY] = False
            person.save(update_fields=("meta",))

        return False


@shared_task(max_retries=2, bind=True)
def update_telegram_groups(self, pk):
    with transaction.atomic():
        try:
            instance = TelegramGroup.objects.select_for_update().get(pk=pk)
        except TelegramGroup.DoesNotExist:
            return

        with instance.admin_session.create_client() as client:
            in_chat_numbers = set(
                member.user.phone_number
                for chat_id in instance.telegram_ids
                for member in client.iter_chat_members(chat_id)
            )

            chat_empty_slots = {
                chat_id: 50 - client.get_chat_members_count(chat_id)
                for chat_id in instance.telegram_ids
            }

            in_segment_and_chat_people = [
                person
                for person in instance.segment.get_people()
                if str(person.contact_phone)[1:] in in_chat_numbers
            ]
            in_segment_not_chat_people = [
                person
                for person in instance.segment.get_people()
                if person.contact_phone
                and is_mobile_number(person.contact_phone)
                and str(person.contact_phone)[1:] not in in_chat_numbers
            ]

            client.import_contacts(
                [
                    InputPhoneContact(
                        phone=str(person.contact_phone),
                        first_name=person.first_name,
                        last_name=person.last_name,
                    )
                    for person in in_segment_not_chat_people
                ]
            )

            new_chat_members = [
                person
                for person in in_segment_not_chat_people
                if is_telegram_user(client, person)
            ]

            def chat_generator():
                for chat_id in instance.telegram_ids:
                    yield chat_id

                while True:
                    title = f"{instance.name} {len(instance.telegram_ids) + 1}"
                    if instance.type == TelegramGroup.CHAT_TYPE_SUPERGROUP:
                        chat_id = client.create_supergroup(title=title).id
                        client.set_chat_permissions(chat_id, DEFAULT_GROUP_PERMISSIONS)
                    elif instance.type == TelegramGroup.CHAT_TYPE_CHANNEL:
                        chat_id = client.create_channel(title=title).id
                    instance.telegram_ids = instance.telegram_ids + [chat_id]
                    chat_empty_slots[chat_id] = 200
                    sleep(5)
                    yield chat_id

            def new_chat_members_generator():
                remaining = new_chat_members
                chat_iterator = chat_generator()
                while len(remaining) > 0:
                    chat_id = next(chat_iterator)
                    while len(remaining) > 0 and chat_empty_slots[chat_id] > 0:
                        to_yield = remaining[: chat_empty_slots[chat_id]]
                        remaining = remaining[chat_empty_slots[chat_id] :]
                        yield chat_id, [str(p.contact_phone) for p in to_yield]

            for chat_id, phones_to_add in new_chat_members_generator():
                client.add_chat_members(chat_id, phones_to_add)
                sleep(5)
                chat_empty_slots[chat_id] = 200 - client.get_chat_members_count(chat_id)

        TelegramGroup.objects.filter(pk=pk).update(
            telegram_ids=instance.telegram_ids,
            telegram_users=len(new_chat_members) + len(in_segment_and_chat_people),
        )
