from django.urls import path

from production.views import ListProductionView, CreateProductionView, ProductionReportView, GenerateReportView


app_name = 'production'


urlpatterns = [
    path('', ListProductionView.as_view(), name='index'),
    path('create/', CreateProductionView.as_view(), name='create'),
    path('report/', ProductionReportView.as_view(), name='report'),
    path('generate-report/', GenerateReportView.as_view(), name='generate-report')
]
