# Generated by Django 3.2.23 on 2024-01-24 10:34

from django.db import migrations

media_tags = [
    ("media__email", "E-mail"),
    ("media__sms", "SMS"),
    ("media__whatsapp", "WhatsApp"),
    ("media__telegram", "Telegram"),
    ("media__courrier", "Courrier"),
]


def create_media_tags(apps, schema):
    PersonTag = apps.get_model("people", "PersonTag")

    for tag, description in media_tags:
        PersonTag.objects.update_or_create(
            label=tag, defaults={"description": description}
        )


def remove_media_tags(apps, schema):
    PersonTag = apps.get_model("people", "PersonTag")

    for tag, _description in media_tags:
        PersonTag.objects.filter(label=tag).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0031_remove_unused_options_for_newsletters"),
    ]

    operations = [
        migrations.RunPython(create_media_tags, reverse_code=remove_media_tags)
    ]
