from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from ingredients.forms import IngredientForm
from ingredients.models import Ingredient
from products.models import Product


class IngredientListView(ListView):
    model = Ingredient
    template_name = 'ingredients/ingredients-list.html'

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        selected_product = request.session.get('selected_product')
        ingredients = Ingredient.objects.filter(product_id=selected_product)

        return render(request, self.template_name, {
            'products': products,
            'selected_product': int(selected_product) if selected_product else None,
            'ingredients': ingredients if selected_product else None
        })

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product')
        # Сохраняется ID, т.к. объект Product not serializable
        request.session['selected_product'] = product_id
        ingredients = Ingredient.objects.filter(product_id=product_id).select_related(
            'product', 'material'
        )

        return render(request, self.template_name, context={
            'ingredients': ingredients,
            'products': Product.objects.all(),
            'selected_product': int(product_id) if product_id else None
        })


class CreateIngredientView(CreateView):
    model = Ingredient
    template_name = 'ingredients/ingredients-create.html'
    form_class = IngredientForm
    success_url = reverse_lazy('ingredients:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {'product': self.request.session['selected_product']}
        return kwargs


class UpdateIngredientView(UpdateView):
    model = Ingredient
    template_name = 'ingredients/ingredients-update.html'
    form_class = IngredientForm
    success_url = reverse_lazy('ingredients:index')


class DeleteIngredientView(DeleteView):
    model = Ingredient
    template_name = 'ingredients/ingredients-delete.html'
    success_url = reverse_lazy('ingredients:index')



