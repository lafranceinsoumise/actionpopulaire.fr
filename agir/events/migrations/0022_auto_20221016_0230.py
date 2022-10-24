# Generated by Django 3.2.14 on 2022-10-16 00:30

import django.core.validators
from django.db import migrations, models
import dynamic_filenames
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0021_auto_20220324_1258"),
    ]

    operations = [
        migrations.AlterField(
            model_name="calendar",
            name="image",
            field=stdimage.models.StdImageField(
                blank=True,
                force_min_size=False,
                upload_to=dynamic_filenames.FilePattern(
                    filename_pattern="{app_label}/{model_name}/{instance.name:slug}{ext}"
                ),
                variations={"banner": (1200, 400), "thumbnail": (400, 250)},
                verbose_name="bannière",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="image",
            field=stdimage.models.StdImageField(
                blank=True,
                force_min_size=False,
                help_text="Vous pouvez ajouter une image de bannière : elle apparaîtra sur la page, et sur les réseaux sociaux en cas de partage. Préférez une image à peu près deux fois plus large que haute. Elle doit faire au minimum 1200 pixels de large et 630 de haut pour une qualité optimale.",
                upload_to=dynamic_filenames.FilePattern(
                    filename_pattern="{app_label}/{model_name}/{instance.id}/banner/{uuid:base32}{ext}"
                ),
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "gif", "png", "svg"]
                    )
                ],
                variations={"banner": (1200, 400), "thumbnail": (400, 250)},
                verbose_name="image",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="report_image",
            field=stdimage.models.StdImageField(
                blank=True,
                force_min_size=False,
                help_text="Cette image apparaîtra en tête de votre compte-rendu, et dans les partages que vous ferez du compte-rendu sur les réseaux sociaux.",
                upload_to=dynamic_filenames.FilePattern(
                    filename_pattern="{app_label}/{model_name}/{instance.id}/report_banner{ext}"
                ),
                variations={"banner": (1200, 400), "thumbnail": (400, 250)},
                verbose_name="image de couverture",
            ),
        ),
        migrations.AlterField(
            model_name="eventimage",
            name="image",
            field=stdimage.models.StdImageField(
                force_min_size=False,
                upload_to=dynamic_filenames.FilePattern(
                    filename_pattern="events/event/{instance.event_id}/{uuid:s}{ext}"
                ),
                variations={
                    "admin_thumbnail": (100, 100, True),
                    "thumbnail": (200, 200, True),
                },
                verbose_name="Fichier",
            ),
        ),
        migrations.AlterField(
            model_name="eventsubtype",
            name="default_image",
            field=stdimage.models.StdImageField(
                blank=True,
                force_min_size=False,
                help_text="L'image associée par défaut à un événement de ce sous-type.",
                upload_to=dynamic_filenames.FilePattern(
                    filename_pattern="{app_label}/{model_name}/{instance.id}/banner/{uuid:base32}{ext}"
                ),
                variations={"banner": (1200, 400), "thumbnail": (400, 250)},
                verbose_name="image par défaut",
            ),
        ),
        migrations.AlterField(
            model_name="eventsubtype",
            name="related_project_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("CON", "Conférence de presse"),
                    ("REU", "Réunion publique et meetings"),
                    ("REU-loc", "Réunion publique organisée localement"),
                    ("REU-ora", "Réunion publique avec un orateur national"),
                    ("REU-can", "Réunion publique avec un candidat"),
                    ("REU-mee", "Meeting"),
                    ("DEB", "Débats et conférences"),
                    ("DEB-aso", "Débat organisé par une association"),
                    ("DEB-con", "Conférence"),
                    ("DEB-caf", "Café-débat"),
                    ("DEB-pro", "Projection et débat"),
                    ("MAN", "Manifestations et événements publics"),
                    ("MAN-loc", "Manifestation ou marche organisée localement"),
                    ("MAN-nat", "Manifestation ou marche nationale"),
                    ("MAN-pic", "Pique-nique ou apéro citoyen"),
                    ("MAN-eco", "Écoute collective"),
                    ("MAN-fet", "Fête (auberge espagnole)"),
                    ("MAN-car", "Caravane"),
                    ("ACT", "Autres actions publiques"),
                    ("TEL", "Émission ou débat télévisé"),
                    ("EVE", "Événements spécifiques"),
                    ("EVE-AMF", "AMFiS d'été"),
                    ("EVE-CON", "Convention"),
                    ("INT", "Evenement Interne"),
                    ("INT-for", "Formation"),
                    ("RH", "Dépenses RH mensuelles"),
                ],
                default="",
                max_length=10,
                verbose_name="Type de projet de gestion associé",
            ),
        ),
    ]