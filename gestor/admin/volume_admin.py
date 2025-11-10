
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    ChoicesDropdownFilter,
)
from unfold.decorators import display

from gestor.models import VolumenTerraceria

@admin.register(VolumenTerraceria)
class VolumenTerraceriaAdmin(ModelAdmin):
    list_display = [
        'nombre',
        'proyecto_link',
        'metodo_badge',
        'area_display',
        'volumenes_display',
        'balance_badge',
        'fecha_calculo_display',
    ]

    list_filter = [
        ('metodo_calculo', ChoicesDropdownFilter),
        ('fecha_calculo', RangeDateFilter),
        ('proyecto', admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = ['nombre', 'descripcion', 'proyecto__codigo']

    readonly_fields = ['fecha_calculo', 'grafica_volumenes', 'resumen_calculo']

    fieldsets = (
        ('Información General', {
            'fields': ('proyecto', 'nombre', 'descripcion', 'metodo_calculo'),
        }),
        ('Resultados', {
            'fields': (
                'area_m2',
                ('volumen_corte_m3', 'volumen_relleno_m3'),
                'volumen_neto_m3',
                'grafica_volumenes',
                'resumen_calculo',
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

    @display(description="Proyecto")
    def proyecto_link(self, obj):
        url = reverse('admin:gestor_proyecto_change', args=[obj.proyecto.pk])
        return format_html('<a href="{}">{}</a>', url, obj.proyecto.codigo)

    @display(description="Método", ordering="metodo_calculo")
    def metodo_badge(self, obj):
        icons = {
            'SECCIONES': '📊',
            'GRID': '⊞',
            'TIN': '▲',
            'CURVAS': '〰️',
        }
        return format_html(
            '{} {}',
            icons.get(obj.metodo_calculo, '📐'),
            obj.get_metodo_calculo_display()
        )

    @display(description="Área", ordering="area_m2")
    def area_display(self, obj):
        return format_html(
            '<strong>{}</strong> m²',
            f'{obj.area_m2:,.0f}'
        )

    @display(description="Volúmenes")
    def volumenes_display(self, obj):
        return format_html(
            '''
            <div style="font-size: 0.875rem;">
                <div style="color: #dc2626;">⬇️ Corte: {} m³</div>
                <div style="color: #2563eb;">⬆️ Relleno: {} m³</div>
            </div>
            ''',
            f'{obj.volumen_corte_m3:,.0f}',
            f'{obj.volumen_relleno_m3:,.0f}'
        )

    @display(description="Balance", ordering="volumen_neto_m3")
    def balance_badge(self, obj):
        neto = obj.volumen_neto_m3
        if abs(neto) < 100:
            return mark_safe(
                '<span class="badge badge-success">✓ Compensado</span>'
            )
        elif neto > 0:
            return format_html(
                '<span class="badge badge-danger">⬇️ Corte +{} m³</span>',
                f'{neto:,.0f}'
            )
        else:
            return format_html(
                '<span class="badge badge-primary">⬆️ Relleno {} m³</span>',
                f'{abs(neto):,.0f}'
            )

    @display(description="Fecha", ordering="fecha_calculo")
    def fecha_calculo_display(self, obj):
        return obj.fecha_calculo.strftime('%d/%m/%Y %H:%M')

    @display(description="Gráfica de Volúmenes")
    def grafica_volumenes(self, obj):
        corte = obj.volumen_corte_m3
        relleno = obj.volumen_relleno_m3
        total = corte + relleno

        porc_corte = (corte / total * 100) if total > 0 else 0
        porc_relleno = (relleno / total * 100) if total > 0 else 0

        return format_html(
            '''
            <div style="margin: 1rem 0;width: 100%;">
                <div style="display: flex; height: 40px; border-radius: 8px; overflow: hidden;width: 100%;">
                    <div style="background: #dc2626;width: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        {}%
                    </div>
                    <div style="background: #2563eb;width: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        {}%
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.875rem;">
                    <div>🔴 Corte: {} m³</div>
                    <div>🔵 Relleno: {} m³</div>
                </div>
            </div>
            ''',
            f'{porc_corte:.0f}', f'{porc_corte:.0f}',
            f'{porc_relleno:.0f}', f'{porc_relleno:.0f}',
            f'{corte:.0f}', f'{relleno:.0f}'
        )

    @display(description="Resumen del Cálculo")
    def resumen_calculo(self, obj):

        # 1. MANEJO DE VALORES NONE (LA CORRECCIÓN DEL ERROR)
        #    Convertimos los números a strings de forma segura,
        #    mostrando 'N/A' si el valor es None.

        area_str = f'{obj.area_m2:,.0f}' if obj.area_m2 is not None else 'N/A'
        corte_str = f'{obj.volumen_corte_m3:,.2f}' if obj.volumen_corte_m3 is not None else 'N/A'
        relleno_str = f'{obj.volumen_relleno_m3:,.2f}' if obj.volumen_relleno_m3 is not None else 'N/A'
        metodo_str = obj.get_metodo_calculo_display()

        # 2. Lógica de balance (necesita su propia comprobación de None)
        neto = obj.volumen_neto_m3
        if neto is not None:
            neto_str = f'{abs(neto):,.2f}'
            tipo_balance_str = 'Compensado' if abs(neto) < 100 else ('Corte' if neto > 0 else 'Relleno')

            # Asignar un color al badge
            if tipo_balance_str == 'Compensado':
                badge_color = 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
            elif tipo_balance_str == 'Corte':
                badge_color = 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
            else:  # Relleno
                badge_color = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'

        else:
            neto_str = 'N/A'
            tipo_balance_str = 'N/A'
            badge_color = 'bg-base-100 text-base-800 dark:bg-base-700 dark:text-base-300'

        # 3. HTML MEJORADO (USANDO CLASES DE UNFOLD/TAILWIND)
        #    Reemplazamos 'style' con clases 'class' para que
        #    funcione con el modo oscuro y los estilos de Unfold.
        return format_html(
            '''
            <div class="p-4 rounded-lg bg-base-50 dark:bg-base-900">
                <h4 class="mt-0 mb-3 text-base font-semibold text-base-900 dark:text-base-100">
                    Resumen Ejecutivo
                </h4>
                <table class="w-full text-sm">
                    <tbody class="divide-y divide-base-200 dark:divide-base-700">
                        <tr class="">
                            <td class="py-2.5 pr-2 font-medium text-base-600 dark:text-base-300">Área procesada:</td>
                            <td class="py-2.5 text-base-900 dark:text-base-100">{} m²</td>
                        </tr>
                        <tr class="">
                            <td class="py-2.5 pr-2 font-medium text-base-600 dark:text-base-300">Volumen de corte:</td>
                            <td class="py-2.5 text-red-600 dark:text-red-500 font-medium">{} m³</td>
                        </tr>
                        <tr class="">
                            <td class="py-2.5 pr-2 font-medium text-base-600 dark:text-base-300">Volumen de relleno:</td>
                            <td class="py-2.5 text-blue-600 dark:text-blue-500 font-medium">{} m³</td>
                        </tr>
                        <tr class="">
                            <td class="py-2.5 pr-2 font-medium text-base-600 dark:text-base-300">Volumen neto:</td>
                            <td class="py-2.5 font-bold text-base-900 dark:text-base-100">{} m³</td>
                        </tr>
                        <tr class="">
                            <td class="py-2.5 pr-2 font-medium text-base-600 dark:text-base-300">Tipo de balance:</td>
                            <td class="py-2.5">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {}">
                                    {}
                                </span>
                            </td>
                        </tr>
                        <tr class="">
                            <td class="py-2.5 pr-2 font-medium text-base-600 dark:text-base-300">Método de cálculo:</td>
                            <td class="py-2.5 text-base-900 dark:text-base-100">{}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            ''',
            area_str,
            corte_str,
            relleno_str,
            neto_str,
            badge_color,  # Pasamos las clases del badge
            tipo_balance_str,
            metodo_str
        )