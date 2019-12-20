from django.db import migrations

# Copié depuis 0014_monthlyallocation_subscription
old_monthlyallocations_trigger_function = """
CREATE OR REPLACE FUNCTION check_subscription_when_allocations_modified() RETURNS TRIGGER AS
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
"""

new_monthlyallocations_trigger_function = """
CREATE OR REPLACE FUNCTION check_subscription_when_allocations_modified() RETURNS TRIGGER AS
$check_allocations$
    DECLARE
        all_allocations_sum INTEGER;
        subscription_total INTEGER;
    BEGIN
        SELECT
            COALESCE(SUM(donations_monthlyallocation.amount), 0), payments_subscription.price
            INTO all_allocations_sum, subscription_total
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

        -- La nouvelle allocation n'est pas encore insérée / mise à jour, donc il faut ajouter son montant
        all_allocations_sum := all_allocations_sum + NEW.amount;
        IF TG_OP = 'UPDATE' THEN
            -- Si c'est un update, l'ancienne version est toujours dans la base : il ne faut donc la retirer
            -- pour éviter de la prendre en compte.
            all_allocations_sum := all_allocations_sum - OLD.amount;
        END IF;

        IF all_allocations_sum > subscription_total THEN
            RAISE integrity_constraint_violation;
        END IF;
    RETURN NEW;
      END
$check_allocations$ LANGUAGE plpgsql;
"""


class Migration(migrations.Migration):
    dependencies = [("donations", "0018_fix_operations_triggers")]

    operations = [
        migrations.RunSQL(
            sql=new_monthlyallocations_trigger_function,
            reverse_sql=old_monthlyallocations_trigger_function,
        )
    ]
