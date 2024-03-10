from django.contrib import admin

from employees.models import Employee, Position, Salary


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_filter = ('year', 'month', 'is_issued')
