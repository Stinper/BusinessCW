from django.urls import path

from procurements.views import ProcurementsListView, ProcurementsCreateView


app_name = 'procurements'


urlpatterns = [
    path('', ProcurementsListView.as_view(), name='index'),
    path('create/', ProcurementsCreateView.as_view(), name='create')
]