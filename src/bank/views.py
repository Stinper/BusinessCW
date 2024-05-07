import datetime
from typing import Collection, Any

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView

from bank.forms import PaymentForm, CreditForm
from bank.models import Payment, Credit
from bank.services.credit import CreditService
from bank.services.payment import PaymentService
from budget.models import Budget
from utils.forms import DateRangeForm
from utils.views import ReportViewMixin, GenerateReportMixin


class PaymentsListView(LoginRequiredMixin, PermissionRequiredMixin,ListView):
    model = Payment
    template_name = 'bank/payments-list.html'
    permission_required = 'bank.view_payment'

    def get(self, request, *args, **kwargs):
        credit_id = request.session.get('credit_id')

        context = self.get_context_data(credit_id=credit_id)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        credit_id: int = request.POST.get('credit')
        request.session['credit_id'] = credit_id

        context = self.get_context_data(credit_id=credit_id)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context: dict = \
            {
                'payments': PaymentService.get_payments_list(kwargs.get('credit_id')),
                'credit_list': CreditService.get_credit_list(),
                'credit_id': kwargs.get('credit_id')
            }

        return context


class CreatePaymentView(LoginRequiredMixin, PermissionRequiredMixin,CreateView):
    model = Payment
    template_name = 'bank/payments-create.html'
    form_class = PaymentForm
    success_url = reverse_lazy('bank:index')
    permission_required = 'bank.add_payment'

    def get_initial(self):
        credit_id = self.request.session.get('credit_id')
        date_string: str = self.form_class.base_fields['date'].initial
        date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

        payment = PaymentService.calculate_payment(date, credit_id)

        initial = {
            'credit_id': payment[0],
            'amount': payment[2],
            'percent': payment[3],
            'general_amount': payment[4],
            'days_overdue': payment[5],
            'penalties': payment[6],
            'total': payment[7],
            'remains': payment[8]
        }

        return initial

    def form_valid(self, form):
        total: float = form.cleaned_data['total']

        if Budget.objects.is_enough_budget(total):
            Budget.objects.decrease_budget(total)

            form.instance.credit_id = self.request.session.get('credit_id')
            return super().form_valid(form)
        else:
            form.add_error('total', 'Для платежа на такую сумму бюджета недостаточно')
            return self.form_invalid(form)


class CreateCreditView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Credit
    template_name = 'bank/credit-create.html'
    form_class = CreditForm
    success_url = reverse_lazy('bank:index')
    permission_required = 'bank.add_credit'

    def form_valid(self, form):
        amount: float = form.cleaned_data['amount']
        Budget.objects.increase_budget(amount)

        return super().form_valid(form)


class PaymentReportView(LoginRequiredMixin, PermissionRequiredMixin, ReportViewMixin, ListView):
    model = Payment
    template_name = 'bank/report-view.html'
    permission_required = 'bank.view_payment'

    session_start_date_name = 'payment_start_date'
    session_end_date_name = 'payment_end_date'

    def get_context_data(self, /, start_date=None, end_date=None, **kwargs):
        context: dict = {
            'date_range_form': DateRangeForm()
        }

        credit_id: int = self.request.session.get('credit_id')

        if start_date and end_date and credit_id:
            context['payments'] = PaymentService.get_payments_list_between_dates(credit_id, start_date, end_date)
            context['date_range_form'].initial = {'start_date': str(start_date), 'end_date': str(end_date)}

        return context


class GenerateReportView(LoginRequiredMixin, PermissionRequiredMixin, GenerateReportMixin, View):
    permission_required = 'employees.view_salary'
    model = Payment
    session_start_date_name = PaymentReportView.session_start_date_name
    session_end_date_name = PaymentReportView.session_end_date_name
    redirect_name = 'bank:index'
    report_main_header = 'Отчет по выдаче заработной платы'

    def get_record_set(self, start_date: str, end_date: str) -> Collection[Collection[Any]]:
        credit_id: int = self.request.session.get('credit_id')
        return PaymentService.get_payments_list_between_dates(credit_id, start_date, end_date)
