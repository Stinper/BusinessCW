from django.db import migrations


def create_procedures_and_functions(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            CREATE FUNCTION IsEnoughMaterialsToCreateProduct(
                ProductID BIGINT,
                ProductAmount INTEGER
            )
            RETURNS INTEGER AS $$
            DECLARE result INTEGER;
            
            BEGIN
                IF EXISTS(SELECT materials_material.ID 
                         FROM ingredients_ingredient INNER JOIN
                         materials_material ON materials_material.ID = ingredients_ingredient.material_id
                         WHERE ingredients_ingredient.product_id = ProductID AND 
                               ingredients_ingredient.amount * ProductAmount > materials_material.amount) THEN
                    result := 0;
                ELSE
                    result := 1;
                END IF;
                
                RETURN result;
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE FUNCTION Create_Production(
                Prod_ID BIGINT,
                Product_Amount INTEGER,
                Production_Date DATE,
                Employee_ID BIGINT
            )
            RETURNS INTEGER AS $$
            DECLARE 
                Is_Created INTEGER;
                final_product_cost FLOAT;
            BEGIN
                IF isenoughmaterialstocreateproduct(Prod_ID, Product_Amount) = 1 THEN
                    INSERT INTO production_production (product_id, amount, date, employee_id)
                    VALUES (Prod_ID, Product_Amount, Production_Date, Employee_ID);
                    
                    WITH total_sum_table AS (
                        UPDATE materials_material AS m
                        SET amount = m.amount - i.amount * product_amount,
                            sum = m.sum - ((m.sum / m.amount) * i.amount * product_amount)
                        FROM ingredients_ingredient AS i
                        WHERE m.id = i.material_id AND i.product_id = prod_id
                        RETURNING ((m.sum / m.amount) * i.amount * product_amount) AS total_sum
                    )
                    
                    SELECT SUM(total_sum) INTO final_product_cost FROM total_sum_table;
                    
                    UPDATE products_product
                    SET amount = amount + product_amount,
                        sum = sum + final_product_cost
                    WHERE id = prod_id;
                    
                    Is_Created := 1;
                ELSE
                    is_created := 0;
                END IF;
                
                RETURN is_created;
                
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE FUNCTION get_productions_list()
            RETURNS TABLE (id bigint, product character varying, amount float, production_date date, employee character varying)
            AS $$
            BEGIN
                RETURN QUERY
            
                SELECT
                    production_production.id,
                    products_product.name,
                    production_production.amount,
                    production_production.date,
                    employees_employee."FIO"
                FROM production_production
                INNER JOIN products_product ON products_product.id = production_production.product_id
                INNER JOIN employees_employee ON employees_employee.id = production_production.employee_id;
                
            END;
            $$ LANGUAGE plpgsql;
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('production', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_procedures_and_functions)
    ]
