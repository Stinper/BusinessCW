from django.urls import path

from products.views import ListProductsView, CreateProductView, UpdateProductView, DeleteProductView


app_name = 'products'


urlpatterns = [
    path('', ListProductsView.as_view(), name='index'),
    path('create/', CreateProductView.as_view(), name='create'),
    path('update/<int:pk>', UpdateProductView.as_view(), name='update'),
    path('delete/<int:pk>', DeleteProductView.as_view(), name='delete')
]
