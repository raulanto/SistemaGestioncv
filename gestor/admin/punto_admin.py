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
from django.db.models import Avg

@admin.register(PuntoControl)
class PuntoControlAdmin(ModelAdmin):
    list_display = [
        'numero_punto',
        'tipo_badge',
        'proyecto_link',
        'elemento_link',
        'equipo_badge',
        'precision_display',
        'display_validador',
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
    change_list_template = "admin/gestor/puntocontrol/change_list.html"
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

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        if hasattr(response, 'context_data'):
            cl = response.context_data.get('cl')
            if cl:
                # El queryset ya respeta los filtros aplicados en la barra lateral de Unfold
                queryset = cl.queryset

                # 1. Conteo total de estaciones/puntos
                total_puntos = queryset.count()

                # 2. Puntos aprobados y validados por el supervisor
                validados = queryset.filter(validado=True).count()

                # 3. Puntos críticos que requieren revisión urgente
                pendientes = queryset.filter(validado=False).count()

                # 4. Promedio del error o precisión horizontal del equipo (GPS, Estación Total)
                precision_stats = queryset.aggregate(Avg('precision_horizontal'))
                avg_precision_h = precision_stats['precision_horizontal__avg'] or 0

                # Enviar las variables calculadas al contexto de la vista HTML
                response.context_data.update({
                    'kpi_total_puntos': total_puntos,
                    'kpi_validados': validados,
                    'kpi_pendientes': pendientes,
                    'kpi_precision_h': round(avg_precision_h, 2),
                })

        return response
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

    # Mantenemos la optimización de base de datos intacta
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("validado_por", "elemento", "proyecto")

    # 1. Agregamos header=True al decorador
    @display(description="Control de Calidad", header=True)
    def display_validador(self, obj):
        if obj.validado:
            user = obj.validado_por
            if user:
                # Obtenemos nombre completo o username
                nombre = user.get_full_name() or user.username
                # Calculamos iniciales automáticas (Ej: "Raul Antonio" -> "RA")
                partes = nombre.split()
                iniciales = "".join(p[0] for p in partes[:2]).upper() if partes else "US"
            else:
                nombre = "Aprobado por Sistema"
                iniciales = "SY"

            # 2. Retornamos la estructura estricta de 4 posiciones de Unfold
            return [
                nombre,  # Posición 0: Título Principal en negritas
                "Aprobado Técnico",  # Posición 1: Subtítulo en gris claro
                iniciales,  # Posición 2: Iniciales (se usan si no hay foto)
                {  # Posición 3: Diccionario de configuración de imagen
                    # Si los usuarios tuvieran un campo de foto (ej. user.perfil.foto.url)
                    # lo pondrías en 'path'. Al poner None, Unfold dibujará un círculo de
                    # color moderno con las iniciales dentro.
                    "path": None,
                    "height": 24,  # Tamaño del avatar (se recomienda 24 o 32)
                    "width": 24,
                    "borderless": False,
                }
            ]

        # 3. Estado de interfaz cuando el punto aún no se aprueba
        return [
            "En Espera",
            "Por Validar",
            "?",
            {
                "path": None,
                "height": 24,
                "width": 24,
                "borderless": True,
            }
        ]
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
