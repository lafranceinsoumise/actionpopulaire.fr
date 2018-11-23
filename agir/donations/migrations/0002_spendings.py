from django.db import migrations, models
import django.db.models.deletion

add_spending_triggers = """
CREATE FUNCTION check_spendings(group_id groups_supportgroup.id%TYPE, new_value INTEGER) RETURNS VOID AS $check_spendings$
    DECLARE
        total INTEGER;
        current INTEGER;
    BEGIN
        total := new_value;

        FOR current IN SELECT da.amount FROM donations_donationallocation AS da
                INNER JOIN payments_payment AS p ON da.payment_id = p.id WHERE da.group_id = check_spendings.group_id AND p.status = 1
                LOOP
            total = total + current;
        END LOOP; 

        FOR current IN SELECT sp.amount FROM donations_spending AS sp WHERE sp.group_id = check_spendings.group_id LOOP
            total = total - current;
        END LOOP; 

        IF total < 0 THEN
            RAISE integrity_constraint_violation;
        END IF;
    END;
$check_spendings$ LANGUAGE plpgsql;

CREATE FUNCTION check_spendings_when_spending_modified() RETURNS TRIGGER AS 
$check_spendings$
    DECLARE
        former_amount INTEGER;
    BEGIN
        IF TG_OP = 'INSERT' THEN
            former_amount := 0;
        ELSE 
            former_amount := OLD.amount;
        END IF;

        PERFORM check_spendings(NEW.group_id, former_amount - NEW.amount);
        RETURN NEW;
      END
$check_spendings$ LANGUAGE plpgsql;

CREATE FUNCTION check_spendings_when_allocation_modified() RETURNS TRIGGER AS 
$check_spendings$
    DECLARE
        new_amount INTEGER;
    BEGIN
        IF TG_OP = 'DELETE' THEN
            new_amount := 0;
        ELSE
            new_amount := NEW.amount;
        END IF;

        PERFORM check_spendings(OLD.group_id, new_amount - OLD.amount );
        RETURN NEW;
      END
$check_spendings$ LANGUAGE plpgsql;


CREATE TRIGGER check_spendings_when_spending_modified BEFORE INSERT OR UPDATE ON donations_spending
    FOR EACH ROW EXECUTE PROCEDURE check_spendings_when_spending_modified();
CREATE TRIGGER check_spendings_when_allocation_modified BEFORE UPDATE OR DELETE ON donations_donationallocation
    FOR EACH ROW EXECUTE PROCEDURE check_spendings_when_allocation_modified();
"""


remove_spending_triggers = """
DROP TRIGGER check_spendings_when_allocation_modified ON donations_donationallocation;
DROP TRIGGER check_spendings_when_spending_modified ON donations_spending;
DROP FUNCTION check_spendings_when_allocation_modified();
DROP FUNCTION check_spendings_when_spending_modified();
DROP FUNCTION check_spendings(groups_supportgroup.id%TYPE, INTEGER);
"""


class Migration(migrations.Migration):
    dependencies = [
        ('donations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Spending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(editable=False, verbose_name="dépense en centimes d'euros")),
                ('group', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT,
                                            to='groups.SupportGroup')),
            ],
        ),
        migrations.RunSQL(
            sql=add_spending_triggers,
            reverse_sql=remove_spending_triggers,
        )
    ]
