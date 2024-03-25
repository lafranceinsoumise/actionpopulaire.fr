# Generated by Django 3.2.24 on 2024-03-22 11:37

import uuid

import django.core.validators
import django.utils.timezone
from django.db import migrations, models

import agir.lib.storage
import agir.lib.validators
import agir.msgs.models


class Migration(migrations.Migration):
    dependencies = [
        ("msgs", "0013_supportgroupmessagerecipient_muted"),
    ]

    operations = [
        migrations.CreateModel(
            name="MessageAttachment",
            fields=[
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="UUID interne à l'API pour identifier la ressource",
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Nom")),
                (
                    "file",
                    models.FileField(
                        storage=agir.lib.storage.OverwriteStorage(),
                        upload_to=agir.msgs.models.message_attachment_upload_to,
                        validators=[
                            agir.lib.validators.FileSizeValidator(10485760),
                            django.core.validators.FileExtensionValidator(
                                [
                                    "pdf",
                                    "doc",
                                    "docx",
                                    "odt",
                                    "xls",
                                    "xlsx",
                                    "ods",
                                    "ppt",
                                    "pptx",
                                    "odp",
                                    "png",
                                    "jpeg",
                                    "jpg",
                                    "gif",
                                ]
                            ),
                        ],
                        verbose_name="Fichier",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pièce-jointe",
                "verbose_name_plural": "Pièces-jointes",
                "ordering": ("created",),
            },
        ),
        migrations.RemoveField(
            model_name="supportgroupmessage",
            name="image",
        ),
        migrations.RemoveField(
            model_name="supportgroupmessagecomment",
            name="image",
        ),
        migrations.AddField(
            model_name="supportgroupmessage",
            name="attachment",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="supportgroupmessages",
                related_query_name="supportgroupmessage",
                to="msgs.messageattachment",
                verbose_name="Pièce-jointe",
            ),
        ),
        migrations.AddField(
            model_name="supportgroupmessagecomment",
            name="attachment",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="supportgroupmessagecomments",
                related_query_name="supportgroupmessagecomment",
                to="msgs.messageattachment",
                verbose_name="Pièce-jointe",
            ),
        ),
    ]
