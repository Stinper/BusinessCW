from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import connection
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from ingredients.forms import IngredientForm
from ingredients.models import Ingredient


class IngredientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Ingredient
    template_name = 'ingredients/ingredients-list.html'
    permission_required = 'ingredients.view_ingredient'

    def get(self, request, *args, **kwargs):
        selected_product = request.session.get('selected_product')

        context = self.get_context_data(product_id=selected_product)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        product_id: int = int(request.POST.get('product'))
        request.session['selected_product'] = product_id

        context = self.get_context_data(product_id=product_id)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context: dict = {}
        product_id: int = kwargs.get('product_id')
        context['selected_product'] = product_id

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM get_products_list()")
            context['products'] = cursor.fetchall()

        if product_id:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_ingredients_for_product(%(product_id)s, %(product_amount)s)",
                               {
                                   'product_id': product_id,
                                   'product_amount': 1
                               })
                context['ingredients'] = cursor.fetchall()
        else:
            context['ingredients'] = None

        return context


class CreateIngredientView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Ingredient
    template_name = 'ingredients/ingredients-create.html'
    form_class = IngredientForm
    success_url = reverse_lazy('ingredients:index')
    permission_required = 'ingredients.add_ingredient'

    def form_valid(self, form):
        with connection.cursor() as cursor:
            cursor.execute("CALL create_ingredient(%(amount)s, %(material_id)s, %(product_id)s)",
                           {
                               'amount': form.cleaned_data['amount'],
                               'material_id': form.instance.material_id,
                               'product_id': form.instance.product_id
                           })

        return redirect('ingredients:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {'product': self.request.session['selected_product']}
        return kwargs


class UpdateIngredientView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Ingredient
    template_name = 'ingredients/ingredients-update.html'
    form_class = IngredientForm
    success_url = reverse_lazy('ingredients:index')
    permission_required = 'ingredients.change_ingredient'

    def form_valid(self, form):
        with connection.cursor() as cursor:
            cursor.execute("CALL update_ingredient(%(id)s, %(amount)s, %(material_id)s, %(product_id)s)",
                           {
                               'id': form.instance.id,
                               'amount': form.cleaned_data['amount'],
                               'material_id': form.instance.material_id,
                               'product_id': form.instance.product_id
                           })

        return redirect('ingredients:index')


class DeleteIngredientView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Ingredient
    template_name = 'ingredients/ingredients-delete.html'
    success_url = reverse_lazy('ingredients:index')
    permission_required = 'ingredients.delete_ingredient'

    def delete(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("CALL delete_ingredient(%(id)s)",
                           {
                               'id': self.get_object().id
                           })

        return redirect('ingredients:index')



