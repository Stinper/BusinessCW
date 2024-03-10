from django.urls import path

from products.views import ListProductsView, CreateProductView


app_name = 'products'


urlpatterns = [
    path('', ListProductsView.as_view(), name='index'),
    path('create/', CreateProductView.as_view(), name='create')
]