from django.db import models


class Credit(models.Model):
    amount = models.PositiveIntegerField('Сумма')
    term = models.PositiveSmallIntegerField('Срок')
    annual_percent = models.PositiveIntegerField('Процент годовых', default=20)
    penalties = models.PositiveIntegerField('Пени', default=2)
    date = models.DateField('Дата получения')

    class Meta:
        verbose_name = 'Кредит'
        verbose_name_plural = 'Кредиты'

    def __str__(self):
        return f'{self.amount} сом, на срок: {self.term} мес., дата выдачи: {self.date}'


class Payment(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.PROTECT, verbose_name='Кредит', related_name='payments')
    date = models.DateField('Дата')
    amount = models.FloatField('Основная сумма')
    percent = models.FloatField('Процент')
    general_amount = models.FloatField('Общая сумма')
    days_overdue = models.PositiveIntegerField('Просрочено дней')
    penalties = models.FloatField('Пени')
    total = models.FloatField('Итого')
    remains = models.FloatField('Остаток')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f'{self.total}: {self.date}'
