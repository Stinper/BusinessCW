from django.db import models

from materials.models import UnitOfMeasurement


class ProductManager(models.Manager):
    def is_enough_product(self, product_id: int, amount: float) -> bool:
        try:
            product = self.get(id=product_id)
            return product.amount >= amount
        except Product.DoesNotExist:
            return False


class Product(models.Model):
    name = models.CharField('Название', max_length=64)
    unit_of_measure = models.ForeignKey(
        UnitOfMeasurement,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Единица измерения'
    )
    amount = models.FloatField('Количество')
    sum = models.FloatField('Сумма')

    objects = ProductManager()

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name
