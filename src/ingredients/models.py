from django.db import models

from materials.models import Material
from products.models import Product


class Ingredient(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='ingredients',
        verbose_name='Продукт'
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name='ingredients',
        verbose_name='Сырье'
    )
    amount = models.FloatField('Количество')

    class Meta:
        verbose_name = 'Интредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = ['product', 'material']

    def __str__(self):
        return f'{self.product}: {self.material} - {self.amount}'

