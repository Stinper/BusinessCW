from django.urls import path

from procurements.views import (ProcurementsListView, ProcurementsCreateView,
                                ProcurementsReportView, GenerateReportView)


app_name = 'procurements'


urlpatterns = [
    path('', ProcurementsListView.as_view(), name='index'),
    path('create/', ProcurementsCreateView.as_view(), name='create'),
    path('report/', ProcurementsReportView.as_view(), name='report'),
    path('generate-report/', GenerateReportView.as_view(), name='generate-report')
]
