from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from materials.forms import MaterialForm
from materials.models import Material


class MaterialListView(ListView):
    model = Material
    template_name = 'materials/materials-list.html'
    context_object_name = 'materials'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materials'] = Material.objects.all().select_related('unit_of_measure')
        return context


class CreateMaterialView(CreateView):
    model = Material
    template_name = 'materials/materials-create.html'
    form_class = MaterialForm
    success_url = reverse_lazy('materials:index')
