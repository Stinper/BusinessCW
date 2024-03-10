from django.db.models import F, When, Value, Case, Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from ingredients.models import Ingredient
from production.forms import ProductionForm
from production.models import Production
from materials.models import Material
from products.models import Product


class ListProductionView(ListView):
    model = Production
    template_name = 'production/production-list.html'
    context_object_name = 'productions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productions'] = Production.objects.all().select_related('product', 'employee')
        return context


class CreateProductionView(CreateView):
    model = Production
    template_name = 'production/production-create.html'
    form_class = ProductionForm
    success_url = reverse_lazy('production:index')

    def form_valid(self, form):
        product_id = form.instance.product_id
        product_amount = form.cleaned_data['amount']

        ingredients = Ingredient.objects.filter(product_id=product_id).select_related('material').annotate(
            need_materials=F('amount') * product_amount,
            need_materials_sum=(F('material__sum') / F('material__amount')) * F('need_materials'),
            is_enough=Case(
                When(material__amount__gte=F('need_materials'), then=Value(True)),
                default=Value(False)
            )
        )

        missing_materials = ingredients.filter(is_enough=False)

        if not missing_materials.exists():
            for ingredient in ingredients:
                ingredient.material.amount -= ingredient.need_materials
                ingredient.material.sum -= ingredient.need_materials_sum
                ingredient.material.save()

            product = Product.objects.get(id=product_id)
            product.amount += product_amount
            product.sum += ingredients.aggregate(total_sum=Sum('need_materials_sum'))['total_sum']
            product.save()

            return super().form_valid(form)

        error_message: str = 'Для производства заданного количества продукции не хватает следующего сырья:'

        for missing_material in missing_materials.values('material__name', 'material__amount', 'need_materials'):
            error_message += (f'\n{missing_material["material__name"]}. '
                              f'Требуется: {missing_material["need_materials"]}, '
                              f'есть на складе: {missing_material["material__amount"]}'
                              )

        form.add_error(field='amount', error=error_message)
        return self.form_invalid(form)
