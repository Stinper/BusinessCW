from budget.models import Budget
from employees.models import Salary, Employee


__all__ = [
    'SalaryService'
]


class SalaryService:
    @staticmethod
    def get_salary_list(year: int, month: int):
        return Salary.objects.filter(year=year, month=month).select_related('employee')

    @staticmethod
    def is_salary_list_exists(year: int, month: int) -> bool:
        return Salary.objects.filter(year=year, month=month).exists()

    @classmethod
    def create_salary_list(cls, year: int, month: int):
        if cls.is_salary_list_exists(year, month):
            return

        employees = Employee.objects.all()
        budget = Budget.objects.get(id=1)

        for employee in employees:
            procurements_count: int = employee.procurements.filter(date__year=year, date__month=month).count()
            production_count: int = employee.productions.filter(date__year=year, date__month=month).count()
            sales_count: int = employee.sales.filter(date__year=year, date__month=month).count()
            common: int = procurements_count + production_count + sales_count
            bonus = common * (budget.bonus / 100) * employee.salary

            Salary.objects.create(
                year=year,
                month=month,
                employee=employee,
                procurements=procurements_count,
                productions=production_count,
                sales=sales_count,
                common=common,
                bonus=bonus,
                general=bonus + employee.salary
            )

    @staticmethod
    def issue_all(salary_list):
        budget = Budget.objects.get(id=1)

        for salary in salary_list:
            budget.budget -= salary.general
            budget.save()

            salary.is_issued = True
            salary.save()

    @staticmethod
    def is_issued(salary_list) -> bool:
        for salary in salary_list:
            if not salary.is_issued:
                return False

        return True
