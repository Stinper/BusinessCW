from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from budget.models import Budget
from products.models import Product
from sales.forms import SalesForm
from sales.models import Sale


class ListSalesView(ListView):
    model = Sale
    template_name = 'sales/sales-list.html'
    context_object_name = 'sales'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sales'] = Sale.objects.all().select_related('product', 'employee')
        return context


class CreateSalesView(CreateView):
    model = Sale
    template_name = 'sales/sales-create.html'
    form_class = SalesForm
    success_url = reverse_lazy('sales:index')

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

