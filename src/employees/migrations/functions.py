from django.db import migrations


def create_procedures_and_functions(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            CREATE FUNCTION get_salary_list(
                target_year int,
                target_month int
            )
            RETURNS TABLE (id BIGINT, year int, month int, employee character varying, procurements_count int, productions_count int, sales_count int,
                          common int, salary int, bonus float, general int, is_issued boolean)
            AS $$
            BEGIN
                RETURN QUERY

                SELECT
				salary.id,
                salary.year,
                salary.month,
				employees."FIO",
                salary.procurements,
                salary.productions,
                salary.sales,
                salary.common,
				employees.salary,
                salary.bonus,
                salary.general,
                salary.is_issued
                FROM employees_salary salary
				INNER JOIN employees_employee employees ON (salary.employee_id = employees.id)
                WHERE salary.year = target_year AND salary.month = target_month;
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE FUNCTION is_salary_list_exists(
                target_year int,
                target_month int
            )
            RETURNS INTEGER
            AS $$
            DECLARE result INTEGER;
            BEGIN

                IF EXISTS(SELECT salary.year
                          FROM employees_salary salary
                          WHERE salary.year = target_year AND salary.month = target_month
                         ) THEN
                    result := 1;
                ELSE
                    result := 0;
                END IF;

                RETURN result;

            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
CREATE PROCEDURE create_salary_list(
                target_year int,
                target_month int
            )
            AS $$
            DECLARE employee RECORD;
            DECLARE budget float;
            DECLARE procurements_count INT;
            DECLARE productions_count INT;
            DECLARE sales_count INT;
            DECLARE common INT;
            DECLARE bonus float;
			DECLARE budget_bonus float;
            BEGIN
                IF is_salary_list_exists(target_year, target_month) = 1 THEN
                    RETURN;
                END IF;

                SELECT b.budget, b.bonus INTO budget, budget_bonus
                FROM budget_budget b
                ORDER BY b.id
                LIMIT 1;

                FOR employee IN SELECT * FROM employees_employee LOOP
                    SELECT COALESCE(COUNT(id), 0) INTO procurements_count
                    FROM procurements_procurement
                    WHERE EXTRACT (YEAR FROM date) = target_year AND
                          EXTRACT (MONTH FROM date) = target_month AND
                          employee_id = employee.id;

                    SELECT COALESCE(COUNT(id), 0) INTO productions_count
                    FROM production_production
                    WHERE EXTRACT (YEAR FROM date) = target_year AND
                          EXTRACT (MONTH FROM date) = target_month AND
                          employee_id = employee.id;

                    SELECT COALESCE(COUNT(id), 0) INTO sales_count
                    FROM sales_sale
                    WHERE EXTRACT (YEAR FROM date) = target_year AND
                          EXTRACT (MONTH FROM date) = target_month AND
                          employee_id = employee.id;

                    common := COALESCE(procurements_count, 0) + COALESCE(productions_count, 0) + COALESCE(sales_count, 0);
                    bonus := common * (budget_bonus / 100.0) * employee.salary;

                    INSERT INTO employees_salary (year, month, employee_id, procurements, productions,
                                                  sales, common, bonus, general, is_issued)
                    VALUES (target_year, target_month, employee.id, procurements_count, productions_count, 
                           sales_count, common, bonus, employee.salary + bonus, FALSE);

                END LOOP;

            END;	
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE FUNCTION get_salary_total_sum (
                target_year int,
                target_month int
            ) RETURNS INT
            AS $$
            DECLARE total_sum int;
            BEGIN
                SELECT SUM(general) INTO total_sum
                FROM employees_salary
                WHERE year = target_year AND
                      month = target_month;

                RETURN total_sum;

            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE PROCEDURE issue_salary_to_all_employees(
                target_year int,
                target_month int
            )
            AS $$
            DECLARE salary_record RECORD;
            DECLARE budget_id int;
            BEGIN

                SELECT b.id INTO budget_id
                FROM budget_budget b
                ORDER BY b.id
                LIMIT 1;

                FOR salary_record IN SELECT * FROM get_salary_list(target_year, target_month) LOOP
                    UPDATE budget_budget 
                    SET budget = budget - salary_record.general
                    WHERE id = budget_id;

                    UPDATE employees_salary
                    SET is_issued = TRUE
                    WHERE id = salary_record.id;
                END LOOP;

            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE PROCEDURE update_salary(
                salary_id BIGINT,
                new_general int
            )
            AS $$
            BEGIN
                UPDATE employees_salary
                SET
                    general = new_general
                WHERE id = salary_id;

            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_salary_list_between_dates(date_from DATE, date_to DATE)
            RETURNS TABLE(id bigint,
                          year integer,
                          month integer,
                          employee character varying,
                          procurements_count integer,
                          productions_count integer,
                          sales_count integer,
                          common integer, 
                          salary integer,
                          bonus double precision,
                          general integer,
                          is_issued boolean) 
            AS 
            $$
                DECLARE from_year INT;
                DECLARE from_month INT;
                DECLARE to_year INT;
                DECLARE to_month INT;
            BEGIN
                from_year := EXTRACT(year FROM date_from)::INTEGER;
                from_month := EXTRACT(month FROM date_from)::INTEGER;
                to_year := EXTRACT(year FROM date_to)::INTEGER;
                to_month := EXTRACT(month FROM date_to)::INTEGER;
                
                
                RETURN QUERY
                
                SELECT
                    salary.id,
                    salary.year,
                    salary.month,
                    employees."FIO",
                    salary.procurements,
                    salary.productions,
                    salary.sales,
                    salary.common,
                    employees.salary,
                    salary.bonus,
                    salary.general,
                    salary.is_issued
                FROM employees_salary salary
                INNER JOIN employees_employee employees ON (salary.employee_id = employees.id)
                WHERE (salary.year BETWEEN from_year AND to_year) AND (salary.month BETWEEN from_month AND to_month);
            END;
            $$ LANGUAGE 'plpgsql'
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_procedures_and_functions)
    ]