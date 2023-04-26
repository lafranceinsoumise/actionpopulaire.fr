# Generated by Django 3.2.18 on 2023-04-04 14:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        (
            "statistics",
            "0002_absolutestatistics_boucle_departementale_membership_person_count",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="MaterielStatistics",
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
                    "date",
                    models.DateField(
                        db_index=True, editable=False, unique=True, verbose_name="Date"
                    ),
                ),
                (
                    "total_orders",
                    models.IntegerField(default=0, verbose_name="Commandes passées"),
                ),
                (
                    "total_items",
                    models.IntegerField(default=0, verbose_name="Produits vendus"),
                ),
                (
                    "total_customer",
                    models.IntegerField(default=0, verbose_name="Clients"),
                ),
                (
                    "total_sales",
                    models.IntegerField(
                        default=0,
                        help_text="Montant indiqué en centîmes d'euros",
                        verbose_name="Ventes brutes",
                    ),
                ),
                (
                    "net_sales",
                    models.IntegerField(
                        default=0,
                        help_text="Montant indiqué en centîmes d'euros",
                        verbose_name="Ventes nettes",
                    ),
                ),
                (
                    "average_sales",
                    models.IntegerField(
                        default=0,
                        help_text="Montant indiqué en centîmes d'euros",
                        verbose_name="Moyenne des ventes nettes par jour",
                    ),
                ),
                (
                    "total_tax",
                    models.IntegerField(
                        default=0,
                        help_text="Montant indiqué en centîmes d'euros",
                        verbose_name="Montant total des taxes",
                    ),
                ),
                (
                    "total_shipping",
                    models.IntegerField(
                        default=0,
                        help_text="Montant indiqué en centîmes d'euros",
                        verbose_name="Montant total des frais de livraison",
                    ),
                ),
                (
                    "total_refunds",
                    models.IntegerField(
                        default=0,
                        help_text="Montant indiqué en centîmes d'euros",
                        verbose_name="Montant total des remboursements",
                    ),
                ),
                (
                    "total_discount",
                    models.IntegerField(
                        default=0,
                        help_text="Montant indiqué en centîmes d'euros",
                        verbose_name="Montant total des code promo utilisés",
                    ),
                ),
            ],
            options={
                "verbose_name": "statistique du site matériel",
                "verbose_name_plural": "statistiques du site matériel",
                "ordering": ("-date",),
                "get_latest_by": "date",
            },
        ),
    ]