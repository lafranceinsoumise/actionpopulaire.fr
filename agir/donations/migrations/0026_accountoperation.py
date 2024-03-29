# Generated by Django 3.2.20 on 2023-11-02 17:01

import agir.donations.model_fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


SQL = """
-- On crée une table temporaire pour mémoriser les associations ancienne opération --> nouvelle opération
CREATE TEMPORARY TABLE operation_reference (operation_id integer, accountoperation_id integer);

INSERT INTO operation_reference (operation_id, accountoperation_id)
(
  SELECT o.id, nextval(pg_get_serial_sequence('donations_accountoperation', 'id'))
  FROM donations_operation AS o
);

-- on crée les nouvelles opérations
INSERT INTO public.donations_accountoperation (id, created, modified, datetime, amount, comment, source, destination, payment_id) 
(
  SELECT
  r.accountoperation_id AS id,
  o.created AS created,
  o.modified AS modified,
  o.created AS datetime,
  ABS(o.amount) AS amount,
  o.comment AS comment,
  CASE 
    WHEN o.amount > 0 THEN 'revenu:dons'
    ELSE 'actif:groupe:' || o.group_id::text
  END as source,
  CASE
    WHEN o.amount > 0 THEN 'actif:groupe:' || o.group_id::text
    ELSE 'depenses'
  END AS destination,
  o.payment_id AS payment_id
  FROM public.donations_operation AS o
  JOIN operation_reference AS r
  ON o.id = r.operation_id
);

UPDATE donations_spendingrequest s
SET account_operation_id = r.accountoperation_id
FROM operation_reference r
WHERE r.operation_id = s.operation_id;


INSERT INTO donations_accountoperation (created, modified, datetime, amount, payment_id, comment, source, destination)
(
  SELECT
  created,
  modified,
  created AS datetime,
  ABS(amount),
  payment_id,
  comment,
  CASE
   WHEN amount > 0 THEN 'revenu:dons'
   ELSE 'actif:cns'
  END AS source,
  CASE
   WHEN amount > 0 THEN 'actif:cns'
   ELSE 'revenu:dons'
  END AS destination
  FROM donations_cnsoperation
);

INSERT INTO donations_accountoperation (created, modified, datetime, amount, payment_id, comment, source, destination)
(
  SELECT
  created,
  modified,
  created AS datetime,
  ABS(amount),
  payment_id,
  comment,
    CASE
   WHEN amount > 0 THEN 'revenu:dons'
   ELSE 'actif:departement:' || departement
  END AS source,
  CASE
   WHEN amount > 0 THEN 'actif:departement:' || departement
   ELSE 'revenu:dons'
  END AS destination
  FROM donations_departementoperation
);
"""


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0018_membership_has_finance_managing_privilege"),
        ("payments", "0004_subscription_month_of_year"),
        ("donations", "0025_auto_20230712_1510"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountOperation",
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
                    "datetime",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Date de l'opération",
                    ),
                ),
                (
                    "amount",
                    agir.donations.model_fields.PositiveBalanceField(
                        verbose_name="montant"
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        help_text="Le compte crédité, celui d'où vient la ressource",
                        max_length=200,
                        verbose_name="Source",
                    ),
                ),
                (
                    "destination",
                    models.CharField(
                        help_text="Le compte débité, celui où va la ressource",
                        max_length=200,
                        verbose_name="Destination",
                    ),
                ),
                ("comment", models.TextField(blank=True, verbose_name="Commentaire")),
                (
                    "payment",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="account_operations",
                        related_query_name="account_operation",
                        to="payments.payment",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="spendingrequest",
            name="account_operation",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="spending_request",
                to="donations.accountoperation",
            ),
        ),
        migrations.RunSQL(sql=SQL, reverse_sql=migrations.RunSQL.noop),
        migrations.AddIndex(
            model_name="accountoperation",
            index=models.Index(
                fields=["source", "destination", "amount"],
                name="donations_accountop_source",
            ),
        ),
        migrations.AddIndex(
            model_name="accountoperation",
            index=models.Index(
                fields=["destination", "amount"], name="donations_accountop_dest"
            ),
        ),
    ]
