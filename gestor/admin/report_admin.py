from django.utils.safestring import mark_safe
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    RangeDateFilter,
)
from unfold.decorators import display
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeNumericFilter,
    ChoicesDropdownFilter,
)
from gestor.models import ReporteAvance

@admin.register(ReporteAvance)
class ReporteAvanceAdmin(ModelAdmin):
    list_display = [
        # 'id',
        'elemento__codigo',
        'fecha_hora_display',
        'avance_display',
        'cuadrilla_display',
        'reportado_por_display',
        'validado_badge',
        'ver_foto',
    ]

    list_filter = [
        'validado',
        ('fecha', RangeDateFilter),
        ('elemento__proyecto', admin.RelatedOnlyFieldListFilter),
        ('avance_porcentaje', RangeNumericFilter),
    ]

    search_fields = ['elemento__codigo', 'descripcion', 'reportado_por__username']

    readonly_fields = [
        'fecha',
        'hora',
        'foto_preview',
        'mapa_ubicacion',
    ]

    fieldsets = (
        ('Información del Reporte', {
            'fields': (
                'elemento',
                'cuadrilla',
                ('fecha', 'hora'),
                'reportado_por',
            ),
            'classes': ['tab'],
        }),
        ('Ubicación', {
            'fields': (
                ('latitud', 'longitud'),
                'mapa_ubicacion',
            ),
            'classes': ['tab'],
        }),
        ('Avance', {
            'fields': (
                'avance_cantidad',
                'avance_porcentaje',
                'descripcion',
            ),
        }),
        ('Recursos', {
            'fields': (
                'materiales_utilizados',
                ('personal_asignado', 'horas_trabajadas'),
            ),
            'classes': ['tab'],
        }),
        ('Evidencia', {
            'fields': (
                'foto',
                'foto_preview',
            ),
            'classes': ['tab'],
        }),
        ('Validación', {
            'fields': (
                'validado',
                'validado_por',
            ),
            'classes': ['tab'],
        }),
    )

    actions = ['validar_reportes', 'exportar_reportes']

    @display(description="Elemento")
    def elemento_codigo(self, obj):
        url = reverse('admin:gestor_elementoconstructivo_change', args=[obj.elemento.pk])
        return format_html('<a href="{}">{}</a>', url, obj.elemento.codigo)

    @display(description="Fecha y Hora", ordering="fecha")
    def fecha_hora_display(self, obj):
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.fecha.strftime('%d/%m/%Y'),
            obj.hora.strftime('%H:%M')
        )

    @display(description="Avance", ordering="avance_porcentaje")
    def avance_display(self, obj):
        color = 'success' if obj.avance_porcentaje >= 80 else 'warning' if obj.avance_porcentaje >= 50 else 'info'
        return format_html(
            '''
            <div style="min-width: 80px;">
                <div class="progress" style="height: 18px;">
                    <div class="progress-bar bg-{}" style="width: {}%">{}%</div>
                </div>
                <small class="text-muted">{} unidades</small>
            </div>
            ''',
            color, f'{obj.avance_porcentaje:,.0f}', f'{obj.avance_porcentaje:,.0f}', f'{obj.avance_cantidad:,.0f}'
        )

    @display(description="Cuadrilla")
    def cuadrilla_display(self, obj):
        if obj.cuadrilla:
            return obj.cuadrilla.nombre
        return format_html('<span class="text-muted">N/A</span>')

    @display(description="Reportado por")
    def reportado_por_display(self, obj):
        if obj.reportado_por:
            return format_html(
                '👤 {}',
                obj.reportado_por.get_full_name() or obj.reportado_por.username
            )
        return '-'

    @display(description="Validado", ordering="validado")
    def validado_badge(self, obj):
        if obj.validado:
            validador = obj.validado_por.get_full_name() if obj.validado_por else 'Sistema'
            return format_html(
                '<span class="badge badge-success" title="Validado por {}">✓</span>',
                validador
            )
        return mark_safe('<span class="badge badge-warning">Pendiente</span>')

    @display(description="Foto")
    def ver_foto(self, obj):
        if obj.foto:
            return format_html(
                '<a href="{}" target="_blank"> Ver</a>',
                obj.foto.url
            )
        return mark_safe('<span class="text-muted">Sin foto</span>')

    @display(description="Vista Previa de Foto")
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-width: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">',
                obj.foto.url
            )
        return mark_safe('<span class="text-muted">Sin foto cargada</span>')

    @display(description="Ubicación del Reporte")
    def mapa_ubicacion(self, obj):
        if not obj.latitud or not obj.longitud:
            return "Sin ubicación"

        return format_html(
            '''
            <div id="map-reporte-{}" style="height: 300px; border-radius: 8px;"></div>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                var map = L.map('map-reporte-{}').setView([{}, {}], 16);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                L.marker([{}, {}]).addTo(map).bindPopup('Reporte: {}');
            </script>
            <p style="margin-top: 0.5rem;">
                <a href="https://www.google.com/maps?q={},{}" target="_blank">
                    Abrir en Google Maps
                </a>
            </p>
            ''',
            obj.pk, obj.pk,
            obj.latitud, obj.longitud,
            obj.latitud, obj.longitud,
            obj.elemento.codigo,
            obj.latitud, obj.longitud
        )

    @admin.action(description="✓ Validar reportes seleccionados")
    def validar_reportes(self, request, queryset):
        updated = queryset.update(
            validado=True,
            validado_por=request.user
        )
        self.message_user(request, f'{updated} reportes validados', 'success')

    @admin.action(description="📄 Exportar reportes a Excel")
    def exportar_reportes(self, request, queryset):
        # Implementar exportación
        self.message_user(request, f'{queryset.count()} reportes exportados', 'success')
