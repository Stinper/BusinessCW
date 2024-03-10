from django.db import models

from materials.models import Material
from employees.models import Employee


class Procurement(models.Model):
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name='procurements',
        verbose_name='Сырье'
    )
    amount = models.FloatField('Количество')
    sum = models.FloatField('Сумма')
    date = models.DateField('Дата', auto_now_add=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='procurements',
        verbose_name='Сотрудник'
    )

    class Meta:
        verbose_name = 'Закупка'
        verbose_name_plural = 'Закупки'

    def __str__(self):
        return f'{self.material}: {self.amount}'
