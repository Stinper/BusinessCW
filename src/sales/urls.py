from django.urls import path

from sales.views import ListSalesView, CreateSalesView


app_name = 'sales'


urlpatterns = [
    path('', ListSalesView.as_view(), name='index'),
    path('create/', CreateSalesView.as_view(), name='create')
]
