from django.db import migrations


def create_procedures_and_functions(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            CREATE FUNCTION get_ingredients_for_product(
              ProductID BIGINT,
              ProductAmount float
            )
            RETURNS TABLE (id BIGINT, name character varying, amount float, cost float, material_id BIGINT)
            AS $$
            BEGIN
              RETURN QUERY

              SELECT
                ingredients.id,
                materials.name,
                ingredients.amount * ProductAmount as amount,
                (materials.sum / materials.amount) * ingredients.amount * ProductAmount as cost,
                materials.id AS material_id
              FROM ingredients_ingredient AS ingredients
              INNER JOIN materials_material AS materials ON ingredients.material_id = materials.id
              WHERE ingredients.product_id = ProductID;
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            CREATE PROCEDURE update_ingredient(
              IngredientID BIGINT,
              new_amount float,
              new_material_id BIGINT,
              new_product_id BIGINT
            )
            AS $$
            BEGIN
              UPDATE ingredients_ingredient
              SET
                amount = new_amount,
                material_id = new_material_id,
                product_id = new_product_id
              WHERE id = IngredientID;
            END;
            $$ LANGUAGE plpgsql;    
        """)

        cursor.execute("""
            CREATE PROCEDURE create_ingredient(
              new_amount float,
              new_material_id BIGINT,
              new_product_id BIGINT
            )
            AS $$
            BEGIN
              INSERT INTO ingredients_ingredient (amount, material_id, product_id)
              VALUES (new_amount, new_material_id, new_product_id);
            END;
            $$ LANGUAGE plpgsql;
        """)
        cursor.execute("""
            CREATE PROCEDURE delete_ingredient(
              IngredientID BIGINT
            )
            AS $$
            BEGIN
              DELETE FROM ingredients_ingredient
              WHERE id = IngredientID;

            END;
            $$ LANGUAGE plpgsql;
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('ingredients', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_procedures_and_functions)
    ]