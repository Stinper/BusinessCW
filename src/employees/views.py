from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db import connection
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from budget.models import Budget
from employees.forms import EmployeeForm, SelectYearMonthForm, SalaryForm
from employees.models import Employee, Salary
from employees.services.salary import SalaryService


class EmployeesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employees-list.html'
    context_object_name = 'employees'
    permission_required = 'employees.view_employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all().select_related('position')

        return context


class CreateEmployeeView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employees-create.html'
    success_url = reverse_lazy('employees:index')
    permission_required = 'employees.add_employee'


class UpdateEmployeeView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employees-update.html'
    success_url = reverse_lazy('employees:index')
    permission_required = 'employees.change_employee'


class DeleteEmployeeView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/employees-delete.html'
    success_url = reverse_lazy('employees:index')
    permission_required = 'employees.delete_employee'


class ListSalaryView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Salary
    template_name = 'employees/salary-list.html'
    context_object_name = 'salaries'
    permission_required = 'employees.view_salary'

    def get(self, request, *args, **kwargs):
        year = request.session.get('year')
        month = request.session.get('month')

        context = self.get_context_data(year=year, month=month)
        request.session['total_sum'] = context['total_sum']

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        year: int = request.POST.get('year')
        month: int = request.POST.get('month')

        request.session['year'] = year
        request.session['month'] = month

        SalaryService.create_salary_list(year, month)
        context = self.get_context_data(year=year, month=month)
        request.session['total_sum'] = context['total_sum']

        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context: dict = {}
        year: int = kwargs['year']
        month: int = kwargs['month']

        context['salaries'] = SalaryService.get_salary_list(year, month)
        context['total_sum'] = SalaryService.get_salary_total_sum(year, month)
        context['choice_form'] = SelectYearMonthForm()
        context['is_issued'] = SalaryService.is_issued(context['salaries'])
        context['is_period_selected'] = bool(year and month)

        if year and month:
            context['choice_form'].initial = {'year': year, 'month': month}

        return context


class UpdateSalaryView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Salary
    template_name = 'employees/salary-update.html'
    form_class = SalaryForm
    success_url = reverse_lazy('employees:salary-index')
    permission_required = 'employees.change_salary'

    def form_valid(self, form):
        with connection.cursor() as cursor:
            cursor.execute("CALL update_salary(%(id)s, %(general)s)",
                           {
                               'id': self.kwargs['pk'],
                               'general': form.cleaned_data['general']
                           })

        return redirect('employees:salary-index')


class IssueSalaryView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'employees.change_salary'

    @staticmethod
    def get(request, *args, **kwargs):
        total_sum = request.session.get('total_sum')
        year: int = request.session.get('year')
        month: int = request.session.get('month')

        if Budget.objects.is_enough_budget(total_sum):
            SalaryService.issue_salary_to_all_employees(year, month)
        else:
            messages.error(request, 'Для выдачи зарплаты всем сотрудникам не хватает бюджета')

        return redirect('employees:salary-index')


