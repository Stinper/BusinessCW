from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from materials.forms import MaterialForm
from materials.models import Material


class MaterialListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Material
    template_name = 'materials/materials-list.html'
    context_object_name = 'materials'
    permission_required = 'materials.view_material'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materials'] = Material.objects.all().select_related('unit_of_measure')
        return context


class CreateMaterialView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Material
    template_name = 'materials/materials-create.html'
    form_class = MaterialForm
    success_url = reverse_lazy('materials:index')
    permission_required = 'materials.add_material'
