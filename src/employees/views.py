from typing import Collection, Any

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import connection
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from budget.models import Budget
from employees.forms import EmployeeForm, SelectYearMonthForm, SalaryForm
from employees.models import Employee, Salary
from employees.services.salary import SalaryService
from utils.forms import DateRangeForm
from utils.views import ReportViewMixin, GenerateReportMixin


class UserLoginView(LoginView):
    template_name = 'employees/user-login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('main:index')


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

    def form_valid(self, form):
        password = form.cleaned_data.get('password')
        form.instance.set_password(password)
        return super().form_valid(form)


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


class SalaryReportView(LoginRequiredMixin, PermissionRequiredMixin, ReportViewMixin, ListView):
    model = Salary
    template_name = 'employees/sales-report-view.html'
    permission_required = 'employees.view_salary'

    session_start_date_name = 'salary_start_date'
    session_end_date_name = 'salary_end_date'

    def get_context_data(self, /, start_date=None, end_date=None, **kwargs):
        context: dict = {
            'date_range_form': DateRangeForm()
        }

        if start_date and end_date:
            context['salaries'] = SalaryService.get_salary_list_between_dates(start_date, end_date)
            context['date_range_form'].initial = {'start_date': str(start_date), 'end_date': str(end_date)}

        return context


class GenerateReportView(LoginRequiredMixin, PermissionRequiredMixin, GenerateReportMixin, View):
    permission_required = 'employees.view_salary'
    model = Salary
    session_start_date_name = SalaryReportView.session_start_date_name
    session_end_date_name = SalaryReportView.session_end_date_name
    redirect_name = 'employees:salary-index'
    report_main_header = 'Отчет по платежам по кредиту'

    def get_record_set(self, start_date: str, end_date: str) -> Collection[Collection[Any]]:
        return SalaryService.get_salary_list_between_dates(start_date, end_date)

    def get_headers_list(cls) -> list:
        return ['ID', 'Год', 'Месяц', 'Сотрудник', 'К-во закупок', 'К-во производств',
                'К-во продаж', 'Общее к-во участий', 'Оклад', 'Бонус', 'Общее', 'Выдано']
