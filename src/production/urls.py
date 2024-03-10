from django.urls import path

from production.views import ListProductionView, CreateProductionView


app_name = 'production'


urlpatterns = [
    path('', ListProductionView.as_view(), name='index'),
    path('create/', CreateProductionView.as_view(), name='create')
]
