from django.db import connection
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from products.forms import ProductForm
from products.models import Product


class ListProductsView(ListView):
    model = Product
    template_name = 'products/products-list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_products_list()")
            result = cursor.fetchall()

        context['products'] = result
        return context


class CreateProductView(CreateView):
    model = Product
    template_name = 'products/products-create.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:index')

    def form_valid(self, form):
        with connection.cursor() as cursor:
            cursor.execute("CALL create_product(%(name)s, %(amount)s, %(sum)s, %(unit_of_measure_id)s)",
                           {
                               'name': form.cleaned_data['name'],
                               'amount': form.cleaned_data['amount'],
                               'sum': form.cleaned_data['sum'],
                               'unit_of_measure_id': form.instance.unit_of_measure_id,
                           })

        return redirect(reverse_lazy('products:index'))


class UpdateProductView(UpdateView):
    model = Product
    template_name = 'products/products-update.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:index')

    def form_valid(self, form):
        with connection.cursor() as cursor:
            cursor.execute("CALL update_product(%(id)s, %(name)s, %(amount)s, %(sum)s, %(unit_of_measure_id)s)",
                           {
                               'id': form.instance.id,
                               'name': form.cleaned_data['name'],
                               'amount': form.cleaned_data['amount'],
                               'sum': form.cleaned_data['sum'],
                               'unit_of_measure_id': form.instance.unit_of_measure_id,
                           })

        return redirect(reverse_lazy('products:index'))


class DeleteProductView(DeleteView):
    model = Product
    template_name = 'products/products-delete.html'
    success_url = reverse_lazy('products:index')

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        with connection.cursor() as cursor:
            cursor.execute("CALL delete_product(%(id)s",
                           {
                               'id': instance.id
                           })
            
        return redirect(reverse_lazy('products:index'))


