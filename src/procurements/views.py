from typing import Collection, Any

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView

from budget.models import Budget
from materials.models import Material
from procurements.forms import ProcurementForm
from procurements.models import Procurement
from utils.forms import DateRangeForm
from utils import TableReportGenerator, get_desktop_path
from utils.views import ReportViewMixin, GenerateReportMixin


class ProcurementsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Procurement
    template_name = 'procurements/procurements-list.html'
    permission_required = 'procurements.view_procurement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['procurements'] = Procurement.objects.all().select_related('material', 'employee')
        return context


class ProcurementsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Procurement
    template_name = 'procurements/procurements-create.html'
    form_class = ProcurementForm
    success_url = reverse_lazy('procurements:index')
    permission_required = 'procurements.add_procurement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget'] = Budget.objects.get(id=1).budget
        return context

    def form_valid(self, form):
        cost_of_procurement: float = form.cleaned_data['sum']

        if Budget.objects.is_enough_budget(cost_of_procurement):
            Budget.objects.decrease_budget(cost_of_procurement)

            material = Material.objects.get(id=form.instance.material_id)
            material.amount += form.cleaned_data['amount']
            material.sum += cost_of_procurement
            material.save()

            return super().form_valid(form)
        else:
            form.add_error(field='sum', error='В бюджете недостаточно средств для покупки на такую сумму')
            return self.form_invalid(form)


class ProcurementsReportView(LoginRequiredMixin, PermissionRequiredMixin, ReportViewMixin, ListView):
    model = Procurement
    template_name = 'procurements/report-view.html'
    permission_required = 'procurements.view_procurement'

    session_start_date_name = 'procurements_start_date'
    session_end_date_name = 'procurements_end_date'

    def get_context_data(self, /, start_date=None, end_date=None, **kwargs):
        context: dict = {
            'date_range_form': DateRangeForm()
        }

        if start_date and end_date:
            procurements = Procurement.objects.filter(date__range=(start_date, end_date))
            context['procurements'] = procurements
            context['date_range_form'].initial = {'start_date': str(start_date), 'end_date': str(end_date)}

        return context


class GenerateReportView(LoginRequiredMixin, PermissionRequiredMixin, GenerateReportMixin, View):
    permission_required = 'procurements.view_procurement'
    model = Procurement
    session_start_date_name = ProcurementsReportView.session_start_date_name
    session_end_date_name = ProcurementsReportView.session_end_date_name
    redirect_name = 'procurements:index'
    report_main_header = 'Отчет по закупкам'

    def get_record_set(self, start_date: str, end_date: str) -> Collection[Collection[Any]]:
        return Procurement.objects.filter(date__range=(start_date, end_date)).values_list(
            'id', 'material__name', 'amount', 'sum', 'date', 'employee__FIO'
        )

    # @staticmethod
    # def post(request, *args, **kwargs):
    #     start_date = request.session.get('procurements_start_date')
    #     end_date = request.session.get('procurements_end_date')
    #     procurements = Procurement.objects.filter(date__range=(start_date, end_date))
    #
    #     doc_name: str = f'procurements-report-{start_date}-{end_date}.docx'
    #     rows_count = procurements.count()
    #     fields = Procurement._meta.fields
    #     headers: list = [field.verbose_name for field in fields]
    #
    #     report = TableReportGenerator(doc_name, rows_count, len(headers), headers)
    #     report.add_header('Отчет по закупкам', 1)
    #     report.add_paragraph(f'С: {start_date}')
    #     report.add_paragraph(f'По: {end_date}')
    #
    #     report.fill_table(procurements.values_list('id', 'material__name', 'amount', 'sum', 'date', 'employee__FIO'))
    #     report.save(f'{get_desktop_path()}\\{doc_name}')
    #
    #     return redirect('procurements:index')
