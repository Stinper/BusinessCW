from django.db import models


class BudgetManager(models.Manager):
    @staticmethod
    def is_enough_budget(amount: float) -> bool:
        try:
            budget = Budget.objects.get(id=1)
            return amount <= budget.budget
        except Budget.DoesNotExist:
            return False

    @staticmethod
    def decrease_budget(amount: float) -> bool:
        try:
            budget = Budget.objects.get(id=1)
            budget.budget -= amount
            budget.save()
            return True
        except Budget.DoesNotExist:
            return False

    @staticmethod
    def increase_budget(amount: float) -> bool:
        return BudgetManager.decrease_budget(-amount)


class Budget(models.Model):
    budget = models.FloatField('Бюджет')
    percent = models.FloatField('Наценка')
    bonus = models.PositiveSmallIntegerField('Бонус')

    objects = BudgetManager()

    class Meta:
        verbose_name = 'Бюджет'

    def __str__(self):
        return str(self.budget)
