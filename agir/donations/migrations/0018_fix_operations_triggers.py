from django.db import migrations

# Copié depuis 0002_spendings
old_operations_trigger_function = """
CREATE OR REPLACE FUNCTION check_spendings_when_operation_modified() RETURNS TRIGGER AS
$check_spendings$
    DECLARE
        former_amount INTEGER;
        former_total INTEGER;
    BEGIN
        IF TG_OP = 'INSERT' THEN
            former_amount := 0;
        ELSE
            former_amount := OLD.amount;
        END IF;


        -- Vérifions que la balance du NOUVEAU groupe est supérieure à zéro
        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
            SELECT COALESCE(SUM(amount), 0) INTO former_total FROM donations_operation WHERE donations_operation.group_id = NEW.group_id;

            -- Le total doit rester supérieur à zéro
            IF former_total - former_amount + NEW.amount < 0 THEN
                RAISE integrity_constraint_violation;
            END IF;
        END IF;

        IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND NEW.group_id <> OLD.group_id) THEN
            SELECT COALESCE(SUM(amount), 0) INTO former_total FROM donations_operation WHERE donations_operation.group_id = OLD.group_id;

            IF former_total - OLD.amount < 0 THEN
                RAISE integrity_constraint_violation;
            END IF;
        END IF;
        RETURN NEW;
      END
$check_spendings$ LANGUAGE plpgsql;
"""


new_operations_trigger_function = """
CREATE OR REPLACE FUNCTION check_spendings_when_operation_modified() RETURNS TRIGGER AS
$check_spendings$
    DECLARE
        group_has_changed BOOLEAN;
        balance INTEGER;
    BEGIN
        group_has_changed := NEW.group_id <> OLD.group_id;
    
        -- Vérifions que la balance du NOUVEAU groupe est supérieure à zéro
        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
            SELECT COALESCE(SUM(amount), 0) INTO balance FROM donations_operation WHERE donations_operation.group_id = NEW.group_id;

            -- On ajoute à ce total la valeur de la nouvelle opération
            balance := balance + NEW.amount;
            
            IF TG_OP = 'UPDATE' AND NOT group_has_changed THEN
                -- Si on a mis à jour une opération (sans changer le groupe), il ne faut pas faire de double
                -- comptage. Le SELECT ci-dessus inclut dans la somme le montant de l'opération avant mise à jour,
                -- qu'il faut donc soustraire à la balance.
                balance := balance - OLD.amount;
            END IF;

            -- Le total doit rester supérieur ou égal à zéro
            IF balance < 0 THEN
                RAISE integrity_constraint_violation;
            END IF;
        END IF;

        -- Vérifions que la balance de l'ANCIEN groupe est supérieure à zéro
        IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND group_has_changed) THEN
            SELECT COALESCE(SUM(amount), 0) INTO balance FROM donations_operation WHERE donations_operation.group_id = OLD.group_id;

            -- On retire à ce total le montant de l'opération qui est supprimée
            balance := balance - OLD.amount;

            IF balance < 0 THEN
                RAISE integrity_constraint_violation;
            END IF;
        END IF;
        RETURN NEW;
      END
$check_spendings$ LANGUAGE plpgsql;
"""


class Migration(migrations.Migration):
    dependencies = [("donations", "0017_fix_payment_triggers")]

    operations = [
        migrations.RunSQL(
            sql=new_operations_trigger_function,
            reverse_sql=old_operations_trigger_function,
        )
    ]
