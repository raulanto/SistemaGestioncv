from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RelatedDropdownFilter, ChoicesDropdownFilter
from gestor.models import Estimacion, EstimacionDetalle
from .finanzas_admin import RetencionInline

class EstimacionDetalleInline(TabularInline):
    model = EstimacionDetalle
    extra = 1
    autocomplete_fields = ['concepto']
    fields = ('concepto', 'cantidad_periodo', 'importe_periodo', 'acumulado_anterior', 'acumulado_actual')
    readonly_fields = ('importe_periodo', 'acumulado_actual')

@admin.register(Estimacion)
class EstimacionAdmin(ModelAdmin):
    list_display = ['numero', 'proyecto', 'periodo_inicio', 'periodo_fin', 'estado', 'autorizada_por']
    search_fields = ['proyecto__codigo', 'proyecto__nombre', 'numero']
    list_filter = [
        ('proyecto', RelatedDropdownFilter),
        ('estado', ChoicesDropdownFilter),
    ]
    autocomplete_fields = ['proyecto', 'autorizada_por']
    inlines = [EstimacionDetalleInline, RetencionInline]
    
    fieldsets = (
        ('Información Principal', {
            'fields': (
                ('proyecto', 'numero'),
                ('periodo_inicio', 'periodo_fin')
            ),
            'classes': ['tab'],
        }),
        ('Control', {
            'fields': (
                'estado',
                'autorizada_por'
            ),
            'classes': ['tab'],
        }),
    )

@admin.register(EstimacionDetalle)
class EstimacionDetalleAdmin(ModelAdmin):
    list_display = ['estimacion', 'concepto', 'cantidad_periodo', 'importe_periodo', 'acumulado_actual']
    search_fields = ['estimacion__numero', 'estimacion__proyecto__codigo', 'concepto__clave']
    list_filter = [
        ('estimacion__proyecto', RelatedDropdownFilter),
        ('estimacion', RelatedDropdownFilter),
    ]
    autocomplete_fields = ['estimacion', 'concepto']
