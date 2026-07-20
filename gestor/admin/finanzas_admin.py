from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RelatedDropdownFilter, ChoicesDropdownFilter
from gestor.models import Retencion, ConvenioModificatorio, GastoReal

class RetencionInline(TabularInline):
    model = Retencion
    extra = 1
    fields = ('tipo', 'descripcion', 'importe')

@admin.register(Retencion)
class RetencionAdmin(ModelAdmin):
    list_display = ['estimacion', 'tipo', 'importe']
    search_fields = ['estimacion__numero', 'estimacion__proyecto__codigo', 'descripcion']
    list_filter = [
        ('tipo', ChoicesDropdownFilter),
        ('estimacion__proyecto', RelatedDropdownFilter),
    ]
    autocomplete_fields = ['estimacion']

@admin.register(ConvenioModificatorio)
class ConvenioModificatorioAdmin(ModelAdmin):
    list_display = ['numero_convenio', 'proyecto', 'fecha_firma', 'ampliacion_monto', 'ampliacion_dias']
    search_fields = ['numero_convenio', 'proyecto__codigo', 'proyecto__nombre']
    list_filter = [
        ('proyecto', RelatedDropdownFilter),
    ]
    autocomplete_fields = ['proyecto']

@admin.register(GastoReal)
class GastoRealAdmin(ModelAdmin):
    list_display = ['proyecto', 'tipo', 'fecha_gasto', 'importe', 'factura']
    search_fields = ['proyecto__codigo', 'concepto__clave', 'descripcion', 'factura']
    list_filter = [
        ('tipo', ChoicesDropdownFilter),
        ('proyecto', RelatedDropdownFilter),
    ]
    autocomplete_fields = ['proyecto', 'concepto']
