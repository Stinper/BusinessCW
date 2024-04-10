import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from bank.forms import PaymentForm, CreditForm
from bank.models import Payment, Credit
from bank.services.credit import CreditService
from bank.services.payment import PaymentService
from budget.models import Budget


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
