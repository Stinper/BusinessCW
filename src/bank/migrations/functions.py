from django.db import migrations


def create_procedures_and_functions(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            CREATE FUNCTION get_credits_list() 
            RETURNS TABLE (ID BIGINT, amount int, term smallint, annual_percent int, penalties int, credit_date date,
                           credit_description text)
            AS $$
            BEGIN
                RETURN QUERY
                
            SELECT
                credit.id,
                credit.amount,
                credit.term,
                credit.annual_percent,
                credit.penalties,
                credit.date,
                credit.amount || ' сом, на срок: ' || credit.term || ' мес, дата выдачи: ' || credit.date AS credit_description
            FROM
                bank_credit credit;
                
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE FUNCTION get_payments_list(target_credit_id BIGINT)
            RETURNS TABLE(id BIGINT, credit_id BIGINT, payment_date date, amount float,
                          percent float, general_amount float, days_overdue int,
                          penalties float, total float, remains float)
            AS $$
            BEGIN
                RETURN QUERY
                
                SELECT
                    payment.id,
                    payment.credit_id,
                    payment.date,
                    payment.amount,
                    payment.percent,
                    payment.general_amount,
                    payment.days_overdue,
                    payment.penalties,
                    payment.total,
                    payment.remains
                FROM
                    bank_payment payment
                WHERE
                    payment.credit_id = target_credit_id;
            
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_overdue(credit_date DATE, payment_date DATE, previous_payment_date DATE DEFAULT NULL)
            RETURNS INTEGER AS $$
            DECLARE
                days_difference INTEGER;
            BEGIN
                IF previous_payment_date IS NOT NULL THEN
                    credit_date := MAKE_DATE(EXTRACT(YEAR FROM credit_date)::INTEGER, EXTRACT(MONTH FROM previous_payment_date)::INTEGER, EXTRACT(DAY FROM credit_date)::INTEGER);
                END IF;
            
                days_difference := (payment_date - credit_date);
            
                RETURN CASE
                    WHEN days_difference > 30 THEN days_difference - 30
                    ELSE 0
                END;
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE FUNCTION calculate_payment(payment_date DATE, cred_id BIGINT)
            RETURNS TABLE (credit_id BIGINT, date DATE, amount float,
                           percent float, general_amount float, days_overdue int, penalties float,
                           total float, remains float)
            AS $$
            DECLARE credit_amount FLOAT;
            DECLARE credit_term int;
            DECLARE credit_annual_percent int;
            DECLARE credit_penalties float;
            DECLARE credit_date DATE;
            
            DECLARE last_payment_date DATE;
            DECLARE last_payment_remains FLOAT;
            
            DECLARE amount FLOAT;
            DECLARE percent FLOAT;
            DECLARE general_amount FLOAT;
            DECLARE penalties FLOAT;
            DECLARE total FLOAT;
            DECLARE remains FLOAT;
            DECLARE days_overdue int;
            BEGIN
                SELECT 
                    credit.amount, credit.term, credit.annual_percent, credit.penalties, credit.date
                INTO
                    credit_amount, credit_term, credit_annual_percent, credit_penalties, credit_date
                FROM
                    bank_credit credit;
                    
                SELECT payment.date, payment.remains INTO last_payment_date, last_payment_remains
                FROM bank_payment payment
                WHERE payment.credit_id = cred_id
                ORDER BY payment.date DESC
                LIMIT 1;
                    
                IF last_payment_date IS NOT NULL THEN
                    days_overdue := (SELECT * FROM get_overdue(credit_date, payment_date, last_payment_date));
                ELSE
                    days_overdue := (SELECT * FROM get_overdue(credit_date, payment_date));
                END IF;
                
                amount := credit_amount / credit_term;
                percent := (credit_amount * (credit_annual_percent / 100.0)) / 12.0;
                general_amount := amount + percent;
                penalties := general_amount * credit_penalties / 100.0 * days_overdue;
                total := general_amount + penalties;
                
                IF last_payment_date IS NOT NULL THEN
                    remains := last_payment_remains - amount;
                ELSE
                    remains := credit_amount - amount;
                END IF;
            
                RETURN QUERY
                
                SELECT
                    cred_id,
                    payment_date,
                    amount,
                    percent,
                    general_amount,
                    days_overdue,
                    penalties,
                    total,
                    remains;
                    
            END;
            $$ LANGUAGE plpgsql;
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('bank', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_procedures_and_functions)
    ]
