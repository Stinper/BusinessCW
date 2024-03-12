from django.db import migrations


def create_functions_and_procedures(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            CREATE PROCEDURE public.create_product(
                IN name character varying,
                IN amount double precision,
                IN sum double precision,
                IN unit_of_measure_id bigint)
            LANGUAGE 'plpgsql'
            AS $BODY$
            BEGIN
                INSERT INTO products_product (name, amount, sum, unit_of_measure_id)
                VALUES (name, amount, sum, unit_of_measure_id);
            END;
            $BODY$;
        """)

        cursor.execute("""
            CREATE PROCEDURE public.update_product(
                IN in_id bigint,
                IN in_name character varying,
                IN in_amount double precision,
                IN in_sum double precision,
                IN in_unit_of_measure_id bigint)
            LANGUAGE 'plpgsql'
            AS $BODY$
             BEGIN
            
                UPDATE products_product
                SET
                    name = in_name,
                    amount = in_amount,
                    sum = in_sum,
                    unit_of_measure_id = in_unit_of_measure_id
                WHERE products_product.id = in_id;
            
            END;
            $BODY$;
        """)

        cursor.execute("""
            CREATE PROCEDURE delete_product(
                in_id BIGINT
            )
            AS
            $$ BEGIN
                DELETE FROM products_product
                WHERE id=in_id;
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE FUNCTION public.get_products_list(
                )
                RETURNS TABLE(id bigint, name character varying, unit_of_measure character varying, amount double precision, sum double precision) 
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000
            
            AS $BODY$
            BEGIN
                RETURN QUERY
                SELECT
                    products_product.id,
                    products_product.name,
                    materials_unitofmeasurement.name as unit_of_measure,
                    products_product.amount,
                    products_product.sum
                FROM
                    products_product 
                INNER JOIN
                    materials_unitofmeasurement 
                ON
                    products_product.unit_of_measure_id = materials_unitofmeasurement.id;
            END
            $BODY$;
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_functions_and_procedures)
    ]
