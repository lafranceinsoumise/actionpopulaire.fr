# Generated by Django 2.2.3 on 2019-07-24 14:28

from django.db import migrations, models
import django.db.models.deletion

add_allocation_triggers = """
CREATE FUNCTION check_subscription_when_allocations_modified() RETURNS TRIGGER AS
$check_allocations$
    DECLARE
        allocations INTEGER;
        subscription INTEGER;
    BEGIN
        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN

            SELECT
                COALESCE(SUM(donations_monthlyallocation.amount), 0), payments_subscription.price
                INTO allocations, subscription
            FROM
                payments_subscription,
                donations_monthlyallocation                
            WHERE
                donations_monthlyallocation.subscription_id = NEW.subscription_id
            AND
                payments_subscription.id = NEW.subscription_id
            GROUP BY
                payments_subscription.id
            ;


            IF allocations - subscription < 0 THEN
                RAISE integrity_constraint_violation;
            END IF;
        END IF;
        RETURN NEW;
      END
$check_allocations$ LANGUAGE plpgsql;

CREATE TRIGGER check_subscription_when_allocations_modified BEFORE INSERT OR UPDATE ON donations_monthlyallocation
    FOR EACH ROW EXECUTE PROCEDURE check_subscription_when_allocations_modified();
"""


remove_allocation_triggers = """
DROP TRIGGER check_subscription_when_allocations_modified ON donations_monthlyallocation;
DROP FUNCTION check_subscription_when_allocations_modified();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("donations", "0013_monthlyallocation"),
        ("payments", "0001_creer_modeles" ""),
    ]

    operations = [
        migrations.AddField(
            model_name="monthlyallocation",
            name="subscription",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="allocations",
                to="payments.Subscription",
            ),
        ),
        migrations.RunSQL(
            sql=add_allocation_triggers, reverse_sql=remove_allocation_triggers
        ),
    ]
