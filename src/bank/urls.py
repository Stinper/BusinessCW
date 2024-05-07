from django.urls import path

from bank.views import (PaymentsListView, CreatePaymentView, CreateCreditView,
                        PaymentReportView, GenerateReportView)


app_name = 'bank'


urlpatterns = [
    path('', PaymentsListView.as_view(), name='index'),
    path('create/', CreatePaymentView.as_view(), name='create-payment'),
    path('new-credit/', CreateCreditView.as_view(), name='new-credit'),
    path('report/', PaymentReportView.as_view(), name='report'),
    path('generate-report/', GenerateReportView.as_view(), name='generate-report')
]
