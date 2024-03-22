from django.db import connection
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from production.forms import ProductionForm
from production.models import Production


class ListProductionView(ListView):
    model = Production
    template_name = 'production/production-list.html'
    context_object_name = 'productions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_productions_list()")
            result = cursor.fetchall()

        context['productions'] = result
        return context


class CreateProductionView(CreateView):
    model = Production
    template_name = 'production/production-create.html'
    form_class = ProductionForm
    success_url = reverse_lazy('production:index')

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
