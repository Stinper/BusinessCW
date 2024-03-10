from django.contrib import admin

from production.models import Production


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    pass