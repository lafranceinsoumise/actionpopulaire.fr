import datetime
import django.contrib.postgres.fields.ranges
from django.db import migrations
from psycopg2._range import DateRange

TABLES = [
    "elus_mandatmunicipal",
    "elus_mandatdepartemental",
    "elus_mandatregional",
]

# Cette extension est nécessaire pour pouvoir créer l'index car les index gist ne supportent
# par le type uuid par défaut.
CREER_EXTENSION_BTREE_GIST = "CREATE EXTENSION IF NOT EXISTS btree_gist;"

DE_DEBUT_FIN_VERS_DATES = """
UPDATE {table}
SET dates = daterange(debut, fin, '[)');
"""

DE_DATES_VERS_DEBUT_FIN = """
UPDATE {table}
SET 
    debut = lower(dates),
    fin = upper(dates);
"""

# Crée une contrainte d'exclusion qui empêche l'existence de deux mandats pour les mêmes
# personnes et conseils si leurs plages de dates se chevauchent (l'opérateur && exprime
# l'intersection)
AJOUTER_EXCLUSION = """
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE {table}
ADD CONSTRAINT {table}_unique_within_dates
EXCLUDE USING gist (person_id WITH =, conseil_id WITH =, dates WITH &&);
"""

RETIRER_EXCLUSION = """
ALTER TABLE {table} DROP CONSTRAINT {table}_unique_within_dates;
"""


# faux défaut
default_date_range = DateRange(
    lower=datetime.date(2000, 1, 1), upper=datetime.date(2000, 1, 2)
)


class Migration(migrations.Migration):
    dependencies = [
        ("elus", "0007_nettoyage_champs"),
    ]

    operations = [
        migrations.RunSQL(
            sql=CREER_EXTENSION_BTREE_GIST, reverse_sql=migrations.RunSQL.noop
        ),
        migrations.AddField(
            model_name="mandatdepartemental",
            name="dates",
            field=django.contrib.postgres.fields.ranges.DateRangeField(
                default=default_date_range,
                help_text="La date de fin correspond à la date théorique de fin du mandat si elle est dans le futur et à la date effective sinon.",
                verbose_name="Début et fin du mandat",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="mandatmunicipal",
            name="dates",
            field=django.contrib.postgres.fields.ranges.DateRangeField(
                default=default_date_range,
                help_text="La date de fin correspond à la date théorique de fin du mandat si elle est dans le futur et à la date effective sinon.",
                verbose_name="Début et fin du mandat",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="mandatregional",
            name="dates",
            field=django.contrib.postgres.fields.ranges.DateRangeField(
                default=default_date_range,
                help_text="La date de fin correspond à la date théorique de fin du mandat si elle est dans le futur et à la date effective sinon.",
                verbose_name="Début et fin du mandat",
            ),
            preserve_default=False,
        ),
        *[
            migrations.RunSQL(
                sql=DE_DEBUT_FIN_VERS_DATES.format(table=table),
                reverse_sql=DE_DATES_VERS_DEBUT_FIN.format(table=table),
            )
            for table in TABLES
        ],
        migrations.RemoveField(
            model_name="mandatdepartemental",
            name="debut",
        ),
        migrations.RemoveField(
            model_name="mandatdepartemental",
            name="fin",
        ),
        migrations.RemoveField(
            model_name="mandatmunicipal",
            name="debut",
        ),
        migrations.RemoveField(
            model_name="mandatmunicipal",
            name="fin",
        ),
        migrations.RemoveField(
            model_name="mandatregional",
            name="debut",
        ),
        migrations.RemoveField(
            model_name="mandatregional",
            name="fin",
        ),
        migrations.AlterUniqueTogether(
            name="mandatdepartemental",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="mandatmunicipal",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="mandatregional",
            unique_together=set(),
        ),
        *[
            migrations.RunSQL(
                sql=AJOUTER_EXCLUSION.format(table=table),
                reverse_sql=RETIRER_EXCLUSION.format(table=table),
            )
            for table in TABLES
        ],
    ]
