from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from budget.models import Budget
from materials.models import Material
from procurements.forms import ProcurementForm
from procurements.models import Procurement


class ProcurementsListView(ListView):
    model = Procurement
    template_name = 'procurements/procurements-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['procurements'] = Procurement.objects.all().select_related('material', 'employee')
        return context


class ProcurementsCreateView(CreateView):
    model = Procurement
    template_name = 'procurements/procurements-create.html'
    form_class = ProcurementForm
    success_url = reverse_lazy('procurements:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget'] = Budget.objects.get(id=1).budget
        return context

    def form_valid(self, form):
        cost_of_procurement: float = form.cleaned_data['sum']

        if Budget.objects.is_enough_budget(cost_of_procurement):
            Budget.objects.decrease_budget(cost_of_procurement)

            material = Material.objects.get(id=form.instance.material_id)
            material.amount += form.cleaned_data['amount']
            material.sum += cost_of_procurement
            material.save()

            return super().form_valid(form)
        else:
            form.add_error(field='sum', error='В бюджете недостаточно средств для покупки на такую сумму')
            return self.form_invalid(form)



