from django.contrib import admin

from budget.models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    pass
