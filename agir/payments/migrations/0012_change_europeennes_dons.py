from django.db import migrations


def change_payment_type_for_european_donations(apps, schema):
    Payment = apps.get_model("payments", "Payment")

    Payment.objects.filter(mode="system_pay_afce", type="don").update(
        type="don_europennes"
    )


def change_payment_type_back_to_donations(apps, schema):
    Payment = apps.get_model("payments", "Payment")

    Payment.objects.filter(type="don_europeennes").update(type="don")


class Migration(migrations.Migration):
    dependencies = [("payments", "0011_auto_20190313_1842")]

    operations = [
        migrations.RunPython(
            code=change_payment_type_for_european_donations,
            reverse_code=change_payment_type_back_to_donations,
        )
    ]
