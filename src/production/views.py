from typing import Collection, Any

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import connection
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView

from production.forms import ProductionForm
from production.models import Production
from utils.forms import DateRangeForm
from utils.views import ReportViewMixin, GenerateReportMixin


class ListProductionView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Production
    template_name = 'production/production-list.html'
    context_object_name = 'productions'
    permission_required = 'production.view_production'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_productions_list()")
            result = cursor.fetchall()

        context['productions'] = result
        return context


class CreateProductionView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Production
    template_name = 'production/production-create.html'
    form_class = ProductionForm
    success_url = reverse_lazy('production:index')
    permission_required = 'production.add_production'

    def form_valid(self, form):
        with connection.cursor() as cursor:
            cursor.execute("SELECT create_production(%(product_id)s, %(product_amount)s, %(date)s, %(employee_id)s)",
                           {
                               'product_id': form.instance.product_id,
                               'product_amount': int(form.cleaned_data['amount']),
                               'date': form.cleaned_data['current_date'],
                               'employee_id': form.instance.employee_id
                           })
            is_created = cursor.fetchall()

        if is_created == [(1,)]:
            return redirect(reverse_lazy('production:index'))

        error_message: str = 'Для производства заданного количества продукции не хватает сырья'
        form.add_error(field='amount', error=error_message)

        return self.form_invalid(form)


class ProductionReportView(LoginRequiredMixin, PermissionRequiredMixin, ReportViewMixin, ListView):
    model = Production
    template_name = 'production/report-view.html'
    permission_required = 'production.view_production'

    session_start_date_name = 'productions_start_date'
    session_end_date_name = 'productions_end_date'

    def get_context_data(self, /, start_date=None, end_date=None, **kwargs):
        context: dict = {
            'date_range_form': DateRangeForm()
        }

        if start_date and end_date:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_productions_list() "
                               "WHERE production_date BETWEEN %(start_date)s AND %(end_date)s",
                               {
                                   'start_date': start_date,
                                   'end_date': end_date
                               })
                context['productions'] = cursor.fetchall()
                context['date_range_form'].initial = {'start_date': str(start_date), 'end_date': str(end_date)}

        return context


class GenerateReportView(LoginRequiredMixin, PermissionRequiredMixin, GenerateReportMixin, View):
    permission_required = 'production.view_production'
    model = Production
    session_start_date_name = ProductionReportView.session_start_date_name
    session_end_date_name = ProductionReportView.session_end_date_name
    redirect_name = 'production:index'
    report_main_header = 'Отчет по производству продукции'

    def get_record_set(self, start_date: str, end_date: str) -> Collection[Collection[Any]]:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_productions_list() "
                           "WHERE production_date BETWEEN %(start_date)s AND %(end_date)s",
                           {
                               'start_date': start_date,
                               'end_date': end_date
                           })
            return cursor.fetchall()
