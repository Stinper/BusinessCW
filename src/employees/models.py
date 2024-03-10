from django.db import models


class Position(models.Model):
    name = models.CharField('Наименование', max_length=64)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


class Employee(models.Model):
    FIO = models.CharField('ФИО', max_length=100)
    position = models.ForeignKey(Position,
                                 on_delete=models.PROTECT,
                                 related_name='employees',
                                 verbose_name='Должность'
                                 )
    salary = models.PositiveIntegerField('Зарплата')
    address = models.CharField('Адрес', max_length=64)
    phone_number = models.CharField('Номер телефона', max_length=10)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.FIO


class Salary(models.Model):
    year = models.PositiveIntegerField('Год')
    month = models.PositiveIntegerField('Месяц')
    employee = models.ForeignKey(Employee,
                                 on_delete=models.PROTECT,
                                 related_name='salaries',
                                 verbose_name='Сотрудник')
    procurements = models.PositiveIntegerField('Количество закупок')
    productions = models.PositiveIntegerField('Количество производств')
    sales = models.PositiveIntegerField('Количество продаж')
    common = models.PositiveIntegerField('Общее количество участий')
    bonus = models.FloatField('Бонус')
    general = models.PositiveIntegerField('К выдаче')
    is_issued = models.BooleanField('Выдано', default=False)

    class Meta:
        verbose_name = 'Зарплата'
        unique_together = ('year', 'month', 'employee')

    def __str__(self):
        return f'{self.year} {self.month} {self.employee} {self.general} {self.is_issued}'


