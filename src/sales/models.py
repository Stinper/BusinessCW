from django.db import models

from products.models import Product
from employees.models import Employee


class Sale(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Продукт'
    )
    amount = models.FloatField('Количество')
    sum = models.FloatField('Сумма')
    date = models.DateField('Дата', auto_now_add=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Сотрудник'
    )

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'

    def __str__(self):
        return f'{self.product}: {self.amount}'
