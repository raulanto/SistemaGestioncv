from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RelatedDropdownFilter
from import_export.admin import ImportExportModelAdmin
from gestor.models import ConceptoPresupuesto
from .resorce.presupuesto_resorce import ConceptoPresupuestoResource

@admin.register(ConceptoPresupuesto)
class ConceptoPresupuestoAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_class = ConceptoPresupuestoResource
    
    list_display = ['clave', 'descripcion_corta', 'unidad', 'cantidad_contratada', 'precio_unitario', 'importe_contratado', 'proyecto']
    search_fields = ['clave', 'descripcion', 'proyecto__nombre', 'proyecto__codigo']
    list_filter = [
        ('proyecto', RelatedDropdownFilter),
        'unidad'
    ]
    autocomplete_fields = ['proyecto']
    
    fieldsets = (
        ('Información General', {
            'fields': (
                ('proyecto', 'clave'),
                'descripcion',
                'unidad'
            ),
            'classes': ['tab'],
        }),
        ('Financiero', {
            'fields': (
                ('cantidad_contratada', 'precio_unitario'),
                'importe_contratado'
            ),
            'classes': ['tab'],
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['tab'],
        }),
    )
    readonly_fields = ['importe_contratado', 'created_at', 'updated_at']

    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = "Descripción"
