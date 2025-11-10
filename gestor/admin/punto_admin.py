from django.contrib import admin
from django.template.loader import render_to_string
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

from gestor.models import PuntoControl


@admin.register(PuntoControl)
class PuntoControlAdmin(ModelAdmin):
    list_display = [
        'numero_punto',
        'tipo_badge',
        'proyecto_link',
        'elemento_link',
        'equipo_badge',
        'precision_display',
        'validado_badge',
        'fecha_medicion_display',
    ]

    list_filter = [
        ('tipo', ChoicesDropdownFilter),
        ('equipo_medicion', ChoicesDropdownFilter),
        'validado',
        ('fecha_medicion', RangeDateFilter),
    ]

    search_fields = ['numero_punto', 'descripcion', 'proyecto__codigo']

    readonly_fields = ['fecha_medicion', 'coordenadas_detalle', 'mapa_punto']

    fieldsets = (
        ('Identificación', {
            'fields': (
                'proyecto',
                'elemento',
                'numero_punto',
                'descripcion',
                'tipo',
            ),
        }),
        ('Medición', {
            'fields': (
                ('latitud', 'longitud', 'elevacion'),
                ('precision_horizontal', 'precision_vertical'),
                'equipo_medicion',
                'topografo',
                'fecha_medicion',
                'coordenadas_detalle',
                'mapa_punto',
            ),
        }),
        ('Validación', {
            'fields': (
                'validado',
                'validado_por',
                'fecha_validacion',
                'observaciones',
            ),
        }),
    )

    actions = ['validar_puntos']

    @display(description="Punto", ordering="numero_punto")
    def numero_punto(self, obj):
        return format_html('<strong>{}</strong>', obj.numero_punto)

    @display(description="Tipo", ordering="tipo")
    def tipo_badge(self, obj):
        icons = {
            'BENCHMARK': '🎯',
            'REPLANTEO': '📍',
            'VERIFICACION': '✓',
            'CONTROL': '📏',
            'LEVANTAMIENTO': '🗺️',
        }
        colors = {
            'BENCHMARK': 'danger',
            'REPLANTEO': 'primary',
            'VERIFICACION': 'success',
            'CONTROL': 'info',
            'LEVANTAMIENTO': 'warning',
        }
        return format_html(
            '<span class="badge badge-{}">{} {}</span>',
            colors.get(obj.tipo, 'secondary'),
            icons.get(obj.tipo, '📌'),
            obj.get_tipo_display()
        )

    @display(description="Proyecto")
    def proyecto_link(self, obj):
        url = reverse('admin:gestor_proyecto_change', args=[obj.proyecto.pk])
        return format_html('<a href="{}">{}</a>', url, obj.proyecto.codigo)

    @display(description="Elemento")
    def elemento_link(self, obj):
        if obj.elemento:
            url = reverse('admin:gestor_elementoconstructivo_change', args=[obj.elemento.pk])
            return format_html('<a href="{}">{}</a>', url, obj.elemento.codigo)
        return format_html('<span class="text-muted">N/A</span>')

    @display(description="Equipo", ordering="equipo_medicion")
    def equipo_badge(self, obj):
        icons = {
            'GPS_DIFERENCIAL': '🛰️',
            'GPS_RTK': '📡',
            'ESTACION_TOTAL': '📐',
            'NIVEL': '🔧',
            'GPS_MOVIL': '📱',
        }
        return format_html(
            '{} {}',
            icons.get(obj.equipo_medicion, '🔧'),
            obj.get_equipo_medicion_display()
        )

    @display(description="Precisión")
    def precision_display(self, obj):
        if obj.precision_horizontal and obj.precision_vertical:
            color_h = 'success' if obj.precision_horizontal <= 2 else 'warning' if obj.precision_horizontal <= 5 else 'danger'
            color_v = 'success' if obj.precision_vertical <= 1 else 'warning' if obj.precision_vertical <= 3 else 'danger'
            return format_html(
                '''
                <div>
                    <span class="badge badge-{}">H: ±{}cm</span>
                    <span class="badge badge-{}">V: ±{}cm</span>
                </div>
                ''',
                color_h, obj.precision_horizontal,
                color_v, obj.precision_vertical
            )
        return mark_safe('<span class="text-muted">No especificada</span>')

    @display(description="Validado", ordering="validado")
    def validado_badge(self, obj):

        if obj.validado:

            context = {
                'text': 'Validado',
                'type': 'success',
                'icon': 'heroicons.outline.check-circle'
            }
        else:

            context = {
                'text': 'Pendiente',
                'type': 'warning',
                'icon': 'heroicons.outline.clock'
            }

        html_badge = render_to_string(
            "unfold/helpers/label.html",
            context
        )

        return format_html("{}", html_badge)

    @display(description="Fecha", ordering="fecha_medicion")
    def fecha_medicion_display(self, obj):
        return format_html(
            '{}',
            obj.fecha_medicion.strftime('%d/%m/%Y %H:%M')
        )

    @display(description="Detalle de Coordenadas")
    def coordenadas_detalle(self, obj):
        return format_html(
            '''
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f8f9fa;">
                    <th style="padding: 0.5rem; text-align: left;">Sistema</th>
                    <th style="padding: 0.5rem; text-align: left;">Coordenadas</th>
                </tr>
                <tr>
                    <td style="padding: 0.5rem;"><strong>WGS84</strong></td>
                    <td style="padding: 0.5rem; font-family: monospace;">
                        Lat: {:.6f}°<br/>
                        Lon: {:.6f}°<br/>
                        Elev: {:.3f}m
                    </td>
                </tr>
                <tr style="background: #f8f9fa;">
                    <td style="padding: 0.5rem;"><strong>Precisión</strong></td>
                    <td style="padding: 0.5rem;">
                        Horizontal: ±{}cm<br/>
                        Vertical: ±{}cm
                    </td>
                </tr>
            </table>
            ''',
            obj.latitud, obj.longitud, obj.elevacion,
            obj.precision_horizontal or 'N/A',
            obj.precision_vertical or 'N/A'
        )

    @display(description="Ubicación en Mapa")
    def mapa_punto(self, obj):
        return format_html(
            '''
            <div id="map-punto-{}" style="height: 300px; border-radius: 8px;"></div>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script>
                var map = L.map('map-punto-{}').setView([{}, {}], 17);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                L.marker([{}, {}]).addTo(map)
                    .bindPopup('<b>{}</b><br/>Tipo: {}<br/>Elev: {}m');
            </script>
            ''',
            obj.pk, obj.pk,
            obj.latitud, obj.longitud,
            obj.latitud, obj.longitud,
            obj.numero_punto, obj.get_tipo_display(), obj.elevacion
        )

    @admin.action(description="✓ Validar puntos seleccionados")
    def validar_puntos(self, request, queryset):
        queryset.update(
            validado=True,
            validado_por=request.user,
            fecha_validacion=timezone.now()
        )
        self.message_user(request, f'{queryset.count()} puntos validados', 'success')
