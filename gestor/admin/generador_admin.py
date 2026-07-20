from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RelatedDropdownFilter
from gestor.models import ElementoConceptoRelacion, NumeroGenerador

class ElementoConceptoRelacionInline(TabularInline):
    model = ElementoConceptoRelacion
    extra = 1
    autocomplete_fields = ['concepto']
    fields = ('concepto', 'cantidad_asignada')

class NumeroGeneradorInline(TabularInline):
    model = NumeroGenerador
    extra = 1
    autocomplete_fields = ['concepto']
    fields = ('concepto', 'cantidad_ejecutada', 'fecha_medicion')

@admin.register(ElementoConceptoRelacion)
class ElementoConceptoRelacionAdmin(ModelAdmin):
    list_display = ['elemento', 'concepto', 'cantidad_asignada']
    search_fields = ['elemento__codigo', 'concepto__clave', 'concepto__descripcion']
    list_filter = [
        ('concepto__proyecto', RelatedDropdownFilter),
    ]
    autocomplete_fields = ['elemento', 'concepto']

@admin.register(NumeroGenerador)
class NumeroGeneradorAdmin(ModelAdmin):
    list_display = ['reporte_avance', 'concepto', 'cantidad_ejecutada', 'fecha_medicion']
    search_fields = ['reporte_avance__elemento__codigo', 'concepto__clave']
    list_filter = [
        ('concepto__proyecto', RelatedDropdownFilter),
    ]
    autocomplete_fields = ['reporte_avance', 'concepto']
