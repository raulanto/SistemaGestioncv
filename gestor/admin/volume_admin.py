from django.contrib import admin
from django.urls import reverse
from django.db.models import Sum
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import RangeDateFilter, ChoicesDropdownFilter
from gestor.models import VolumenTerraceria


@admin.register(VolumenTerraceria)
class VolumenTerraceriaAdmin(ModelAdmin):
    change_list_template = "admin/gestor/volumenterraceria/change_list.html"
    # change_form_template = "admin/gestor/volumenterraceria/change_form.html"
    list_display = [
        'nombre',
        'proyecto_link',
        'metodo_badge',
        'area_display',
        'grafica_volumenes_inline',
        'balance_badge',
        'fecha_calculo_display',
    ]

    list_filter = [
        ('metodo_calculo', ChoicesDropdownFilter),
        ('fecha_calculo', RangeDateFilter),
        ('proyecto', admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = ['nombre', 'descripcion', 'proyecto__codigo']

    readonly_fields = ['fecha_calculo', 'grafica_volumenes_detalle']

    fieldsets = (
        ('Información General', {
            'fields': ('proyecto', 'nombre', 'descripcion', 'metodo_calculo'),
        }),
        ('Resultados', {
            'fields': (
                'area_m2',
                ('volumen_corte_m3', 'volumen_relleno_m3'),
                'volumen_neto_m3',
                'grafica_volumenes_detalle',
            ),
        }),
        ('Datos del Levantamiento', {
            'fields': (
                'archivo_levantamiento',
                'calculado_por',
                'fecha_calculo',
            ),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('proyecto')

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and response.context_data.get('cl'):
            qs = response.context_data['cl'].queryset

            totales = qs.aggregate(
                Sum('volumen_corte_m3'),
                Sum('volumen_relleno_m3'),
                Sum('volumen_neto_m3')
            )

            response.context_data.update({
                'kpi_total_registros': qs.count(),
                'kpi_total_corte': totales['volumen_corte_m3__sum'] or 0,
                'kpi_total_relleno': totales['volumen_relleno_m3__sum'] or 0,
                'kpi_balance_neto': totales['volumen_neto_m3__sum'] or 0,
            })
        return response

    @display(description="Proyecto")
    def proyecto_link(self, obj):
        url = reverse('admin:gestor_proyecto_change', args=[obj.proyecto.pk])
        return format_html(
            '<a href="{}" class="font-semibold text-primary-600 dark:text-primary-400 hover:underline">{}</a>',
            url, obj.proyecto.codigo
        )

    @display(description="Método", label=True)
    def metodo_badge(self, obj):
        colores = {
            'SECCIONES': 'info',
            'GRID': 'primary',
            'TIN': 'warning',
            'CURVAS': 'success',
        }
        return obj.metodo_calculo

    @display(description="Área Topográfica", ordering="area_m2")
    def area_display(self, obj):
        area_formateada = f"{obj.area_m2 or 0:,.0f}"
        return format_html(
            '<span class="font-mono text-sm text-green-900 dark:text-green-400">{} m²</span>',
            area_formateada
        )

    @display(description="Proporción Corte / Relleno")
    def grafica_volumenes_inline(self, obj):
        corte = obj.volumen_corte_m3 or 0
        relleno = obj.volumen_relleno_m3 or 0
        total = corte + relleno

        porc_corte = (corte / total * 100) if total > 0 else 0
        porc_relleno = (relleno / total * 100) if total > 0 else 0

        return format_html(
            '<div class="flex flex-col gap-1 w-48">'
            '   <div class="flex h-1.5 w-full rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">'
            '       <div class="bg-red-500" style="width: {}%;"></div>'
            '       <div class="bg-blue-500" style="width: {}%;"></div>'
            '   </div>'
            '   <div class="flex justify-between text-[10px] font-mono text-gray-500 dark:text-gray-400">'
            '       <span title="Corte"><span class="text-red-500">▼</span> {}</span>'
            '       <span title="Relleno"><span class="text-blue-500">▲</span> {}</span>'
            '   </div>'
            '</div>',
            porc_corte, porc_relleno, f"{corte:,.0f}", f"{relleno:,.0f}"
        )

    @display(description="Balance", ordering="volumen_neto_m3")
    def balance_badge(self, obj):
        neto = obj.volumen_neto_m3 or 0
        if abs(neto) < 100:
            return format_html(
                '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-400 ">✓ Compensado</span>')
        elif neto > 0:
            return format_html(
                '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-400 ">▼ {} m³</span>',
                f"{neto:,.0f}")
        else:
            return format_html(
                '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-400 ">▲ {} m³</span>',
                f"{abs(neto):,.0f}")

    @display(description="Fecha", ordering="fecha_calculo")
    def fecha_calculo_display(self, obj):
        return obj.fecha_calculo.strftime('%d/%m/%Y')

    @display(description="Gráfica Detallada")
    def grafica_volumenes_detalle(self, obj):
        corte = obj.volumen_corte_m3 or 0
        relleno = obj.volumen_relleno_m3 or 0
        total = corte + relleno
        porc_corte = (corte / total * 100) if total > 0 else 0
        porc_relleno = (relleno / total * 100) if total > 0 else 0

        return format_html(
            '<div class="w-full max-w-2xl py-2">'
            '   <div class="flex h-8 w-full rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800 ring-1 ring-gray-900/5 dark:ring-white/10">'
            '       <div class="bg-red-500 flex items-center justify-center text-xs font-bold text-white transition-all" style="width: {}%;">{}%</div>'
            '       <div class="bg-blue-500 flex items-center justify-center text-xs font-bold text-white transition-all" style="width: {}%;">{}%</div>'
            '   </div>'
            '   <div class="flex justify-between mt-3 text-sm font-medium">'
            '       <div class="text-red-700 dark:text-red-400 flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-red-500"></span> Corte Extraído: {} m³</div>'
            '       <div class="text-blue-700 dark:text-blue-400 flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-blue-500"></span> Relleno Aplicado: {} m³</div>'
            '   </div>'
            '</div>',
            porc_corte, f"{porc_corte:.0f}", porc_relleno, f"{porc_relleno:.0f}", f"{corte:,.0f}", f"{relleno:,.0f}"
        )