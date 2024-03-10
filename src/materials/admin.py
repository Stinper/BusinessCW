from django.contrib import admin

from materials.models import Material, UnitOfMeasurement


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    pass


@admin.register(UnitOfMeasurement)
class UnitOfMeasurementAdmin(admin.ModelAdmin):
    pass
