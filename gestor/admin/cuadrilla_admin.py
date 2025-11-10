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

from gestor.models import Cuadrilla


@admin.register(Cuadrilla)
class CuadrillaAdmin(ModelAdmin):
    list_display = [
        'nombre',
        'proyecto_link',
        'jefe_display',
        'elemento_actual_display',
        'ubicacion_display',
        'estado_activo',
        'ultima_actualizacion_display',
    ]

    list_filter = [
        'activa',
        ('proyecto', admin.RelatedOnlyFieldListFilter),
        ('ultima_actualizacion', RangeDateFilter),
    ]

    search_fields = ['nombre', 'jefe_cuadrilla__first_name', 'proyecto__codigo']

    fieldsets = (
        ('Información General', {
            'fields': ('proyecto', 'nombre', 'jefe_cuadrilla', 'activa'),
            'classes': ['tab'],
        }),
        ('Ubicación Actual', {
            'fields': (
                ('latitud_actual', 'longitud_actual'),
                'ultima_actualizacion',
                'elemento_actual',
            ),
            'classes': ['tab'],
        }),
    )

    @display(description="Proyecto")
    def proyecto_link(self, obj):
        url = reverse('admin:gestor_proyecto_change', args=[obj.proyecto.pk])
        return format_html('<a href="{}">{}</a>', url, obj.proyecto.codigo)

    @display(description="Jefe de Cuadrilla")
    def jefe_display(self, obj):
        if obj.jefe_cuadrilla:
            return format_html(
                ' {}',
                obj.jefe_cuadrilla.get_full_name() or obj.jefe_cuadrilla.username
            )
        return mark_safe('<span class="text-muted">Sin jefe</span>')

    @display(description="Trabajando en")
    def elemento_actual_display(self, obj):
        if obj.elemento_actual:
            url = reverse('admin:gestor_elementoconstructivo_change', args=[obj.elemento_actual.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.elemento_actual.codigo
            )
        return mark_safe('<span class="text-muted">Sin asignar</span>')

    @display(description="Ubicación GPS")
    def ubicacion_display(self, obj):
        if obj.latitud_actual and obj.longitud_actual:
            return format_html(
                ' <a href="https://www.google.com/maps?q={},{}" target="_blank">Ver mapa</a>',
                obj.latitud_actual, obj.longitud_actual
            )
        return mark_safe('<span class="text-muted">Sin ubicación</span>')

    @display(description="Estado", ordering="activa")
    def estado_activo(self, obj):
        if obj.activa:
            return mark_safe('<span class="badge badge-success">✓ Activa</span>')
        return mark_safe('<span class="badge badge-secondary">Inactiva</span>')

    @display(description="Última Actualización")
    def ultima_actualizacion_display(self, obj):
        if not obj.ultima_actualizacion:
            return mark_safe('<span class="text-muted">Nunca</span>')

        ahora = timezone.now()
        diferencia = ahora - obj.ultima_actualizacion

        if diferencia.total_seconds() < 300:  # 5 minutos
            return format_html('<span class="badge badge-success">Hace {} min</span>',
                               int(diferencia.total_seconds() / 60))
        elif diferencia.total_seconds() < 3600:  # 1 hora
            return format_html('<span class="badge badge-warning">Hace {} min</span>',
                               int(diferencia.total_seconds() / 60))
        else:
            return format_html('<span class="badge badge-danger">Hace {}h</span>',
                               int(diferencia.total_seconds() / 3600))
