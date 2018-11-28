from django.db import migrations

add_spending_triggers = """
CREATE FUNCTION check_spendings_when_operation_modified() RETURNS TRIGGER AS
$check_spendings$
    DECLARE
        new_amount INTEGER;
        former_amount INTEGER;
        group_id UUID;
        former_total INTEGER;
    BEGIN
        IF TG_OP = 'INSERT' THEN
            former_amount := 0;
        ELSE
            former_amount := OLD.amount;
        END IF;

        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
            SELECT COALESCE(SUM(amount), 0) INTO former_total FROM donations_operation WHERE donations_operation.group_id = NEW.group_id;

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

CREATE TRIGGER check_spendings_when_operation_modified BEFORE INSERT OR UPDATE OR DELETE ON donations_operation
    FOR EACH ROW EXECUTE PROCEDURE check_spendings_when_operation_modified();
"""


remove_spending_triggers = """
DROP TRIGGER check_spendings_when_operation_modified ON donations_operation;
DROP FUNCTION check_spendings_when_operations_modified();
"""


class Migration(migrations.Migration):
    dependencies = [("donations", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql=add_spending_triggers, reverse_sql=remove_spending_triggers
        )
    ]
