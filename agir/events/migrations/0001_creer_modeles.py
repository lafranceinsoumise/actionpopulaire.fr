import agir.lib.form_fields
import agir.lib.model_fields
import agir.lib.models
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import dynamic_filenames
import re
import stdimage.models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("people", "0001_creer_modeles"),
        ("groups", "0001_creer_modeles"),
        ("payments", "0001_creer_modeles"),
    ]

    operations = [
        migrations.CreateModel(
            name="Calendar",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="titre")),
                ("slug", models.SlugField(unique=True, verbose_name="slug")),
                (
                    "archived",
                    models.BooleanField(
                        default=False, verbose_name="Calendrier archivé"
                    ),
                ),
                (
                    "user_contributed",
                    models.BooleanField(
                        default=False,
                        verbose_name="Les utilisateurs peuvent ajouter des événements",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Saisissez une description (HTML accepté)",
                        verbose_name="description",
                    ),
                ),
                (
                    "image",
                    stdimage.models.StdImageField(
                        blank=True,
                        upload_to=dynamic_filenames.FilePattern(
                            filename_pattern="{app_label}/{model_name}/{instance.name:slug}{ext}"
                        ),
                        verbose_name="bannière",
                    ),
                ),
            ],
            options={
                "verbose_name": "Agenda",
            },
        ),
        migrations.CreateModel(
            name="CalendarItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
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
            ],
            options={
                "verbose_name": "Élément de calendrier",
            },
        ),
        migrations.CreateModel(
            name="Event",
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
                (
                    "coordinates",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True,
                        geography=True,
                        null=True,
                        srid=4326,
                        verbose_name="coordonnées",
                    ),
                ),
                (
                    "coordinates_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Coordonnées manuelles"),
                            (10, "Coordonnées automatiques précises"),
                            (
                                20,
                                "Coordonnées automatiques approximatives (niveau rue)",
                            ),
                            (
                                25,
                                "Coordonnées automatique approximatives (arrondissement)",
                            ),
                            (30, "Coordonnées automatiques approximatives (ville)"),
                            (50, "Coordonnées automatiques (qualité inconnue)"),
                            (254, "Pas de position géographique"),
                            (255, "Coordonnées introuvables"),
                        ],
                        editable=False,
                        help_text="Comment les coordonnées ci-dessus ont-elle été acquises",
                        null=True,
                        verbose_name="type de coordonnées",
                    ),
                ),
                (
                    "location_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="nom du lieu"
                    ),
                ),
                (
                    "location_address1",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="adresse (1ère ligne)"
                    ),
                ),
                (
                    "location_address2",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="adresse (2ème ligne)"
                    ),
                ),
                (
                    "location_citycode",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="code INSEE"
                    ),
                ),
                (
                    "location_city",
                    models.CharField(blank=True, max_length=100, verbose_name="ville"),
                ),
                (
                    "location_zip",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="code postal"
                    ),
                ),
                (
                    "location_state",
                    models.CharField(blank=True, max_length=40, verbose_name="état"),
                ),
                (
                    "location_country",
                    django_countries.fields.CountryField(
                        blank=True, default="FR", max_length=2, verbose_name="pays"
                    ),
                ),
                (
                    "contact_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="nom du contact"
                    ),
                ),
                (
                    "contact_email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        verbose_name="adresse email du contact",
                    ),
                ),
                (
                    "contact_phone",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        verbose_name="numéro de téléphone du contact",
                    ),
                ),
                (
                    "contact_hide_phone",
                    models.BooleanField(
                        default=False, verbose_name="Cacher mon numéro de téléphone"
                    ),
                ),
                (
                    "image",
                    stdimage.models.StdImageField(
                        blank=True,
                        help_text="Vous pouvez ajouter une image de bannière : elle apparaîtra sur la page, et sur les réseaux sociaux en cas de partage. Préférez une image à peu près deux fois plus large que haute. Elle doit faire au minimum 1200 pixels de large et 630 de haut pour une qualité optimale.",
                        upload_to=dynamic_filenames.FilePattern(
                            filename_pattern="{app_label}/{model_name}/{instance.id}/banner{ext}"
                        ),
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["jpg", "jpeg", "gif", "png", "svg"]
                            )
                        ],
                        verbose_name="image",
                    ),
                ),
                (
                    "description",
                    agir.lib.models.DescriptionField(
                        blank=True,
                        help_text="Une courte description",
                        verbose_name="description",
                    ),
                ),
                (
                    "allow_html",
                    models.BooleanField(
                        default=False,
                        verbose_name="autoriser le HTML étendu dans la description",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Le nom de l'événement",
                        max_length=255,
                        verbose_name="nom",
                    ),
                ),
                (
                    "visibility",
                    models.CharField(
                        choices=[
                            ("A", "Caché"),
                            ("O", "Visible par les organisateurs"),
                            ("P", "Public"),
                        ],
                        default="P",
                        max_length=1,
                        verbose_name="Visibilité",
                    ),
                ),
                (
                    "start_time",
                    agir.events.models.CustomDateTimeField(
                        verbose_name="date et heure de début"
                    ),
                ),
                (
                    "end_time",
                    agir.events.models.CustomDateTimeField(
                        verbose_name="date et heure de fin"
                    ),
                ),
                (
                    "max_participants",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Nombre maximum de participants",
                    ),
                ),
                (
                    "allow_guests",
                    models.BooleanField(
                        default=False,
                        verbose_name="Autoriser les participant⋅e⋅s à inscrire des invité⋅e⋅s",
                    ),
                ),
                (
                    "facebook",
                    agir.lib.model_fields.FacebookEventField(
                        blank=True,
                        max_length=20,
                        verbose_name="Événement correspondant sur Facebook",
                    ),
                ),
                (
                    "report_image",
                    stdimage.models.StdImageField(
                        blank=True,
                        help_text="Cette image apparaîtra en tête de votre compte-rendu, et dans les partages que vous ferez du compte-rendu sur les réseaux sociaux.",
                        upload_to=dynamic_filenames.FilePattern(
                            filename_pattern="{app_label}/{model_name}/{instance.id}/report_banner{ext}"
                        ),
                        verbose_name="image de couverture",
                    ),
                ),
                (
                    "report_content",
                    agir.lib.models.DescriptionField(
                        blank=True,
                        help_text="Ajoutez un compte-rendu de votre événement. N'hésitez pas à inclure des photos.",
                        verbose_name="compte-rendu de l'événement",
                    ),
                ),
                (
                    "report_summary_sent",
                    models.BooleanField(
                        default=False,
                        verbose_name="Le mail de compte-rendu a été envoyé",
                    ),
                ),
                (
                    "payment_parameters",
                    models.JSONField(
                        blank=True, null=True, verbose_name="Paramètres de paiement"
                    ),
                ),
                (
                    "scanner_event",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="L'ID de l'événement sur le logiciel de tickets",
                    ),
                ),
                (
                    "scanner_category",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="La catégorie que doivent avoir les tickets sur scanner",
                    ),
                ),
                (
                    "enable_jitsi",
                    models.BooleanField(
                        default=False, verbose_name="Activer la visio-conférence"
                    ),
                ),
                (
                    "participation_template",
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name="Template pour la page de participation",
                    ),
                ),
                (
                    "do_not_list",
                    models.BooleanField(
                        default=False,
                        help_text="L'événement n'apparaîtra pas sur la carte, ni sur le calendrier et ne sera pas cherchable via la recherche interne ou les moteurs de recherche.",
                        verbose_name="Ne pas lister l'événement",
                    ),
                ),
                (
                    "legal",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=agir.lib.form_fields.CustomJSONEncoder,
                        verbose_name="Informations juridiques",
                    ),
                ),
                (
                    "for_users",
                    models.CharField(
                        choices=[
                            ("I", "Les insoumis⋅es"),
                            ("2", "Les signataires « Nous Sommes Pour ! »"),
                        ],
                        default="I",
                        max_length=1,
                        verbose_name="Utilisateur⋅ices de la plateforme concerné⋅es par l'événement",
                    ),
                ),
            ],
            options={
                "verbose_name": "événement",
                "verbose_name_plural": "événements",
                "ordering": ("-start_time", "-end_time"),
                "permissions": (
                    ("every_event", "Peut éditer tous les événements"),
                    ("view_hidden_event", "Peut voir les événements non publiés"),
                ),
            },
        ),
        migrations.CreateModel(
            name="EventImage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
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
                    "image",
                    stdimage.models.StdImageField(
                        upload_to=dynamic_filenames.FilePattern(
                            filename_pattern="events/event/{instance.event_id}/{uuid:s}{ext}"
                        ),
                        verbose_name="Fichier",
                    ),
                ),
                ("legend", models.CharField(max_length=280, verbose_name="légende")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EventSubtype",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
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
                    "label",
                    models.CharField(max_length=50, unique=True, verbose_name="nom"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "visibility",
                    models.CharField(
                        choices=[
                            ("N", "Personne (plus utilisé)"),
                            ("D", "Seulement depuis l'administration"),
                            ("A", "N'importe qui"),
                        ],
                        default="D",
                        max_length=1,
                        verbose_name="Qui peut créer avec ce sous-type ?",
                    ),
                ),
                (
                    "hide_text_label",
                    models.BooleanField(
                        default=False, verbose_name="cacher le label texte"
                    ),
                ),
                (
                    "icon",
                    models.ImageField(
                        blank=True,
                        help_text="L'icône associée aux marqueurs sur la carte.",
                        upload_to=dynamic_filenames.FilePattern(
                            filename_pattern="{app_label}/{model_name}/{instance.id}/icon{ext}"
                        ),
                        verbose_name="icon",
                    ),
                ),
                (
                    "icon_name",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        verbose_name="Nom de l'icône Font Awesome",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        blank=True,
                        help_text="La couleur associée aux marqueurs sur la carte.",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                regex="^#[0-9A-Fa-f]{6}$"
                            )
                        ],
                        verbose_name="couleur",
                    ),
                ),
                (
                    "icon_anchor_x",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="ancre de l'icône (x)"
                    ),
                ),
                (
                    "icon_anchor_y",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="ancre de l'icône (y)"
                    ),
                ),
                (
                    "popup_anchor_y",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="placement de la popup (par rapport au point)",
                    ),
                ),
                (
                    "config",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="Configuration"
                    ),
                ),
                (
                    "allow_external",
                    models.BooleanField(
                        default=False,
                        verbose_name="Les non-insoumis⋅es peuvent rejoindre",
                    ),
                ),
                (
                    "external_help_text",
                    models.TextField(
                        blank=True,
                        verbose_name="Phrase d'explication pour rejoindre le groupe ou l'événement",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("G", "Réunion de groupe"),
                            ("M", "Événement public"),
                            ("A", "Action publique"),
                            ("O", "Autre"),
                        ],
                        max_length=1,
                        verbose_name="Type d'événement",
                    ),
                ),
                (
                    "default_description",
                    agir.lib.models.DescriptionField(
                        blank=True,
                        help_text="La description par défaut pour les événements de ce sous-type.",
                        verbose_name="description par défaut",
                    ),
                ),
                (
                    "default_image",
                    stdimage.models.StdImageField(
                        blank=True,
                        help_text="L'image associée par défaut à un événement de ce sous-type.",
                        upload_to=dynamic_filenames.FilePattern(
                            filename_pattern="{app_label}/{model_name}/{instance.id}/banner{ext}"
                        ),
                        verbose_name="image par défaut",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sous-type d'événement",
                "verbose_name_plural": "Sous-types d'événement",
            },
        ),
        migrations.CreateModel(
            name="EventTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "label",
                    models.CharField(max_length=50, unique=True, verbose_name="nom"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
            ],
            options={
                "verbose_name": "tag",
            },
        ),
        migrations.CreateModel(
            name="IdentifiedGuest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("AP", "En attente du paiement"),
                            ("CO", "Inscription confirmée"),
                            ("CA", "Inscription annulée"),
                        ],
                        default="CO",
                        max_length=2,
                        verbose_name="Statut",
                    ),
                ),
            ],
            options={
                "db_table": "events_rsvp_guests_form_submissions",
            },
        ),
        migrations.CreateModel(
            name="JitsiMeeting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "domain",
                    models.CharField(
                        default=agir.events.models.jitsi_default_domain, max_length=255
                    ),
                ),
                (
                    "room_name",
                    models.CharField(
                        default=agir.events.models.jitsi_default_room_name,
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[a-z0-9-_]+$"),
                                "Seulement des lettres minuscules, des chiffres, des _ et des -.",
                                "invalid",
                            )
                        ],
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Début effectif"
                    ),
                ),
                (
                    "end_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Fin effective"
                    ),
                ),
            ],
            options={
                "verbose_name": "Visio-conférence",
            },
        ),
        migrations.CreateModel(
            name="OrganizerConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_creator",
                    models.BooleanField(
                        default=False, verbose_name="Créateur de l'événement"
                    ),
                ),
                (
                    "notifications_enabled",
                    models.BooleanField(
                        default=True, verbose_name="Recevoir les notifications"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RSVP",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
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
                    "guests",
                    models.PositiveIntegerField(
                        default=0, verbose_name="nombre d'invités supplémentaires"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("AP", "En attente du paiement"),
                            ("CO", "Inscription confirmée"),
                            ("CA", "Inscription annulée"),
                        ],
                        default="CO",
                        max_length=2,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "notifications_enabled",
                    models.BooleanField(
                        default=True, verbose_name="Recevoir les notifications"
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rsvps",
                        to="events.event",
                    ),
                ),
            ],
            options={
                "verbose_name": "RSVP",
                "verbose_name_plural": "RSVP",
            },
        ),
        # relations et autres
        migrations.AddField(
            model_name="rsvp",
            name="form_submission",
            field=models.OneToOneField(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rsvp",
                to="people.personformsubmission",
            ),
        ),
        migrations.AddField(
            model_name="rsvp",
            name="guests_form_submissions",
            field=models.ManyToManyField(
                related_name="guest_rsvp",
                through="events.IdentifiedGuest",
                to="people.PersonFormSubmission",
            ),
        ),
        migrations.AddField(
            model_name="rsvp",
            name="jitsi_meeting",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rsvps",
                to="events.jitsimeeting",
            ),
        ),
        migrations.AddField(
            model_name="rsvp",
            name="payment",
            field=models.OneToOneField(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rsvp",
                to="payments.payment",
            ),
        ),
        migrations.AddField(
            model_name="rsvp",
            name="person",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rsvps",
                to="people.person",
            ),
        ),
        migrations.AddField(
            model_name="organizerconfig",
            name="as_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organizer_configs",
                to="groups.supportgroup",
            ),
        ),
        migrations.AddField(
            model_name="organizerconfig",
            name="event",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organizer_configs",
                to="events.event",
            ),
        ),
        migrations.AddField(
            model_name="organizerconfig",
            name="person",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organizer_configs",
                to="people.person",
            ),
        ),
        migrations.AddField(
            model_name="jitsimeeting",
            name="event",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="jitsi_meetings",
                to="events.event",
            ),
        ),
        migrations.AddField(
            model_name="identifiedguest",
            name="payment",
            field=models.OneToOneField(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="identified_guest",
                to="payments.payment",
            ),
        ),
        migrations.AddField(
            model_name="identifiedguest",
            name="rsvp",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="identified_guests",
                to="events.rsvp",
            ),
        ),
        migrations.AddField(
            model_name="identifiedguest",
            name="submission",
            field=models.OneToOneField(
                db_column="personformsubmission_id",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rsvp_guest",
                to="people.personformsubmission",
            ),
        ),
        migrations.AddField(
            model_name="eventimage",
            name="author",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="event_images",
                to="people.person",
            ),
        ),
        migrations.AddField(
            model_name="eventimage",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="events.event",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="attendees",
            field=models.ManyToManyField(
                related_name="events", through="events.RSVP", to="people.Person"
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="organizers",
            field=models.ManyToManyField(
                related_name="organized_events",
                through="events.OrganizerConfig",
                to="people.Person",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="organizers_groups",
            field=models.ManyToManyField(
                related_name="organized_events",
                through="events.OrganizerConfig",
                to="groups.SupportGroup",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="subscription_form",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="people.personform",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="subtype",
            field=models.ForeignKey(
                default=agir.events.models.get_default_subtype,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="events",
                to="events.eventsubtype",
                verbose_name="Sous-type",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="tags",
            field=models.ManyToManyField(
                blank=True, related_name="events", to="events.EventTag"
            ),
        ),
        migrations.AddField(
            model_name="calendaritem",
            name="calendar",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="events.calendar",
            ),
        ),
        migrations.AddField(
            model_name="calendaritem",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="calendar_items",
                to="events.event",
            ),
        ),
        migrations.AddField(
            model_name="calendar",
            name="events",
            field=models.ManyToManyField(
                related_name="calendars",
                through="events.CalendarItem",
                to="events.Event",
            ),
        ),
        migrations.AddField(
            model_name="calendar",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                related_query_name="child",
                to="events.calendar",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="rsvp",
            unique_together={("event", "person")},
        ),
        migrations.AlterUniqueTogether(
            name="identifiedguest",
            unique_together={("rsvp", "submission")},
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(
                fields=["start_time", "end_time"], name="events_datetime_index"
            ),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["end_time"], name="events_end_time_index"),
        ),
    ]
