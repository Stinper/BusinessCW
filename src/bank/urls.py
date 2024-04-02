from django.urls import path

from bank.views import PaymentsListView, CreatePaymentView, CreateCreditView


app_name = 'bank'


urlpatterns = [
    path('', PaymentsListView.as_view(), name='index'),
    path('create/', CreatePaymentView.as_view(), name='create-payment'),
    path('new-credit/', CreateCreditView.as_view(), name='new-credit')
]
