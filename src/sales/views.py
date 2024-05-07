from typing import Collection, Any

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView

from budget.models import Budget
from products.models import Product
from sales.forms import SalesForm
from sales.models import Sale
from utils.forms import DateRangeForm
from utils.views import ReportViewMixin, GenerateReportMixin


class ListSalesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/sales-list.html'
    context_object_name = 'sales'
    permission_required = 'sales.view_sale'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sales'] = Sale.objects.all().select_related('product', 'employee')
        return context


class CreateSalesView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Sale
    template_name = 'sales/sales-create.html'
    form_class = SalesForm
    success_url = reverse_lazy('sales:index')
    permission_required = 'sales.add_sale'

    def form_valid(self, form):
        product_id: int = form.instance.product_id
        amount_of_products: float = form.cleaned_data['amount']

        product: Product = Product.objects.get(id=product_id)

        if product.amount >= amount_of_products:
            sum_: float = (product.sum / product.amount) * amount_of_products
            form.instance.sum = sum_

            product.amount -= amount_of_products
            product.sum -= sum_
            product.save()

            budget = Budget.objects.get(id=1)
            budget.budget += sum_ + (sum_ * (budget.percent / 100))
            budget.save()

            return super().form_valid(form)
        
        form.add_error('amount', f'На складе нет достаточного количества продукции для продажи.'
                                 f' Продукции на складе: {product.amount} {product.unit_of_measure}')
        return self.form_invalid(form)


class SalesReportView(LoginRequiredMixin, PermissionRequiredMixin, ReportViewMixin, ListView):
    model = Sale
    template_name = 'sales/report-view.html'
    permission_required = 'sales.view_sale'

    session_start_date_name = 'sales_start_date'
    session_end_date_name = 'sales_end_date'

    def get_context_data(self, /, start_date=None, end_date=None, **kwargs):
        context: dict = {
            'date_range_form': DateRangeForm()
        }

        if start_date and end_date:
            context['sales'] = Sale.objects.filter(date__range=(start_date, end_date))
            context['date_range_form'].initial = {'start_date': str(start_date), 'end_date': str(end_date)}

        return context


class GenerateReportView(LoginRequiredMixin, PermissionRequiredMixin, GenerateReportMixin, View):
    permission_required = 'sales.view_sale'
    model = Sale
    session_start_date_name = SalesReportView.session_start_date_name
    session_end_date_name = SalesReportView.session_end_date_name
    redirect_name = 'sales:index'
    report_main_header = 'Отчет по продажам продукции'

    def get_record_set(self, start_date: str, end_date: str) -> Collection[Collection[Any]]:
        return Sale.objects.filter(date__range=(start_date, end_date)).values_list(
            'id', 'product__name', 'amount', 'sum', 'date', 'employee__FIO'
        )
