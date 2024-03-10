from django.urls import path

from materials.views import MaterialListView, CreateMaterialView


app_name = 'materials'


urlpatterns = [
    path('', MaterialListView.as_view(), name='index'),
    path('create/', CreateMaterialView.as_view(), name='create')
]