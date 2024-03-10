from django.db import models


class UnitOfMeasurement(models.Model):
    name = models.CharField('Название', max_length=32)

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField('Название', max_length=64)
    unit_of_measure = models.ForeignKey(
        UnitOfMeasurement,
        on_delete=models.PROTECT,
        related_name='materials',
        verbose_name='Единица измерения'
    )
    amount = models.FloatField('Количество')
    sum = models.FloatField('Сумма')

    class Meta:
        verbose_name = 'Сырье'
        verbose_name_plural = 'Сырье'

    def __str__(self):
        return self.name
