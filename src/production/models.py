from django.db import models

from products.models import Product
from employees.models import Employee


class Production(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='productions',
        verbose_name='Продукт'
    )
    amount = models.FloatField('Количество')
    date = models.DateField('Дата', auto_now_add=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='productions',
        verbose_name='Сотрудник'
    )

    class Meta:
        verbose_name = 'Производство'

    def __str__(self):
        return f'{self.product}: {self.amount}'
