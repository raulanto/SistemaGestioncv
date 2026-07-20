from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from unfold.contrib.filters.admin import RelatedDropdownFilter
from gestor.models import Material, InventarioProyecto, MaterialUtilizado

@admin.register(Material)
class MaterialAdmin(ModelAdmin):
    list_display = ['nombre', 'unidad_medida']
    search_fields = ['nombre', 'descripcion']
    list_filter = ['unidad_medida']

    fieldsets = (
        ('Información del Material', {
            'fields': (
                ('nombre', 'unidad_medida'),
                'descripcion',
            ),
            'classes': ['tab'],
        }),
        ('Auditoría', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ['tab'],
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(InventarioProyecto)
class InventarioProyectoAdmin(ModelAdmin):
    list_display = ['material', 'proyecto', 'stock_total_ingresado', 'stock_disponible_display']
    search_fields = ['material__nombre', 'proyecto__nombre', 'proyecto__codigo']
    list_filter = [
        ('proyecto', RelatedDropdownFilter),
        ('material', RelatedDropdownFilter),
    ]
    autocomplete_fields = ['proyecto', 'material']

    fieldsets = (
        ('Asignación de Inventario', {
            'fields': (
                ('proyecto', 'material'),
            ),
            'classes': ['tab'],
        }),
        ('Control de Stock', {
            'fields': (
                ('stock_total_ingresado', 'stock_disponible'),
                'costo_unitario_estimado',
            ),
            'classes': ['tab'],
        }),
        ('Auditoría', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ['tab'],
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    @display(description="Stock Disponible", ordering='stock_disponible')
    def stock_disponible_display(self, obj):
        # Usar colores según disponibilidad (0 = rojo, poco = amarillo, mucho = verde)
        from django.utils.html import format_html
        
        color_class = "text-green-600 dark:text-green-500 font-bold"
        if obj.stock_disponible <= 0:
            color_class = "text-red-600 dark:text-red-500 font-bold"
        elif obj.stock_disponible < (obj.stock_total_ingresado * 0.2):
            color_class = "text-yellow-600 dark:text-yellow-500 font-bold"
            
        return format_html(
            '<span class="{}">{} {}</span>',
            color_class,
            obj.stock_disponible, 
            obj.material.unidad_medida
        )

class MaterialUtilizadoInline(TabularInline):
    model = MaterialUtilizado
    extra = 1
    autocomplete_fields = ['inventario']
    fields = ('inventario', 'cantidad_utilizada', 'notas')
