from django.urls import path

from ingredients.views import IngredientListView, CreateIngredientView, UpdateIngredientView, DeleteIngredientView

app_name = 'ingredients'

urlpatterns = [
    path('', IngredientListView.as_view(), name='index'),
    path('create/', CreateIngredientView.as_view(), name='create'),
    path('update/<int:pk>/', UpdateIngredientView.as_view(), name='update'),
    path('delete/<int:pk>/', DeleteIngredientView.as_view(), name='delete')
]
