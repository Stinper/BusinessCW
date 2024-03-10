from django.contrib import admin

from procurements.models import Procurement


@admin.register(Procurement)
class ProcurementAdmin(admin.ModelAdmin):
    pass
