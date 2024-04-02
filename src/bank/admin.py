from django.contrib import admin
from bank.models import Credit, Payment


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
