from django.contrib import admin

from sales.models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    pass
