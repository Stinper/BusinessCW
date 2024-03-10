from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from products.forms import ProductForm
from products.models import Product


class ListProductsView(ListView):
    model = Product
    template_name = 'products/products-list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all().select_related('unit_of_measure')
        return context


class CreateProductView(CreateView):
    model = Product
    template_name = 'products/products-create.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:index')

