from django.urls import path

from sales.views import ListSalesView, CreateSalesView, SalesReportView, GenerateReportView


app_name = 'sales'


urlpatterns = [
    path('', ListSalesView.as_view(), name='index'),
    path('create/', CreateSalesView.as_view(), name='create'),
    path('report/', SalesReportView.as_view(), name='report'),
    path('generate-report/', GenerateReportView.as_view(), name='generate-report')
]
