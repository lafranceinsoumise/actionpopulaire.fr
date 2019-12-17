from django.db import migrations

# copié depuis 0001_initial
old_payments_triggers = """
CREATE FUNCTION check_allocation_lt_payment() RETURNS TRIGGER AS $process_allocation$
    DECLARE
       payment_amount INTEGER;
    BEGIN
        SELECT price INTO payment_amount FROM payments_payment WHERE id = NEW.payment_id;
        IF payment_amount < NEW.amount THEN
            RAISE EXCEPTION integrity_constraint_violation;
        END IF;
        RETURN NEW;
    END
$process_allocation$ LANGUAGE plpgsql;

CREATE FUNCTION check_payment_gt_allocation() RETURNS TRIGGER AS $process_donation$
    DECLARE 
        allocation INTEGER;
    BEGIN
        SELECT donations_operation.amount INTO allocation FROM donations_operation WHERE payment_id = OLD.id;
        IF allocation IS NOT NULL AND (allocation > NEW.price OR  OLD.id <> NEW.id) THEN
            RAISE EXCEPTION integrity_constraint_violation;
        END IF;
        RETURN NEW;
    END
$process_donation$ LANGUAGE plpgsql;

CREATE TRIGGER check_allocation_lt_payment BEFORE INSERT OR UPDATE ON donations_operation
    FOR EACH ROW EXECUTE PROCEDURE check_allocation_lt_payment();

CREATE TRIGGER check_payment_gt_allocation BEFORE UPDATE ON payments_payment
    FOR EACH ROW EXECUTE PROCEDURE check_payment_gt_allocation();
    
DROP FUNCTION check_operation_for_payment() CASCADE ;
DROP FUNCTION check_payment_operations() CASCADE ;

"""


new_payments_triggers = """
CREATE FUNCTION check_operation_for_payment() RETURNS TRIGGER AS $process_operations$
    DECLARE
        payment_amount INTEGER;
        allocated INTEGER;
    BEGIN
        IF NEW.payment_id IS NULL THEN
            -- on ne contrôle que les opérations associés à des paiement dans cette contrainte
            RETURN NEW;
        END IF;

        IF NEW.amount <= 0 THEN
            -- seules des opérations positives (allocations) peuvent être associées à des paiements
            RAISE integrity_constraint_violation;
        END IF;
        
        SELECT
            p.price, COALESCE(SUM(o.amount), 0)
        INTO
            payment_amount, allocated
        FROM
            payments_payment AS p
        LEFT JOIN
            donations_operation AS o
        ON
            p.id = o.payment_id
        WHERE
            p.id = NEW.payment_id 
        GROUP BY
            p.id;
    
        allocated := allocated + NEW.amount;
        
        IF TG_OP = 'UPDATE' AND OLD.payment_id = NEW.payment_id THEN
            -- si c'est une mise à jour et que l'opération était déjà associé à ce paiement,
            -- on soustrait le vieux montant pour ne pas compter deux fois
            allocated := allocated - OLD.amount;
        END IF;
        
        IF allocated > payment_amount THEN
            RAISE integrity_constraint_violation;
        END IF;
                            
        RETURN NEW;
    END
$process_operations$ LANGUAGE plpgsql;

CREATE FUNCTION check_payment_operations() RETURNS TRIGGER AS $process_donation$
    DECLARE 
        allocations INTEGER;
    BEGIN
        SELECT
            SUM(donations_operation.amount)
        INTO
            allocations
        FROM
            donations_operation
        WHERE
            payment_id = OLD.id;
            
        IF allocations > NEW.price THEN
            RAISE integrity_constraint_violation;
        END IF;
        RETURN NEW;
    END
$process_donation$ LANGUAGE plpgsql;

-- Insertion et mise à jour seulement (car seules des opérations positives sont associés
-- aux paiements, donc pas besoin de contrôler les suppressions)
CREATE TRIGGER check_operation_for_payment BEFORE INSERT OR UPDATE ON donations_operation
    FOR EACH ROW EXECUTE PROCEDURE check_operation_for_payment();

-- Mise à jour seulement (pas d'opérations liées à la création et les clés étrangères
-- gèrent déjà les problématiques de suppression).
CREATE TRIGGER check_payment_operations BEFORE UPDATE ON payments_payment
    FOR EACH ROW EXECUTE PROCEDURE check_payment_operations();

DROP FUNCTION check_allocation_lt_payment() CASCADE ;
DROP FUNCTION check_payment_gt_allocation() CASCADE ;
"""


class Migration(migrations.Migration):
    dependencies = [("donations", "0016_multiple_operations_per_payment")]

    operations = [
        migrations.RunSQL(sql=new_payments_triggers, reverse_sql=old_payments_triggers)
    ]
