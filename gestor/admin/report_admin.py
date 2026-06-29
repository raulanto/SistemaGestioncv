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
from unfold.decorators import display,action
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeNumericFilter,
    ChoicesDropdownFilter,
)
from gestor.models import ReporteAvance
from django.db.models import Avg
from django.shortcuts import redirect
from django.template.loader import render_to_string
from ..forms import ReporteAvanceForm
@admin.register(ReporteAvance)
class ReporteAvanceAdmin(ModelAdmin):
    form = ReporteAvanceForm

    # 2. Inyectar el HTML con los scripts de Leaflet para la vista Edición/Creación
    change_form_template = "admin/gestor/reporteavance/change_form.html"

    # (Opcional pero recomendado) Inyectar el HTML de los KPIs para la tabla
    change_list_template = "admin/gestor/reporteavance/change_list.html"
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

    actions = ['validar_reportes_masivos', 'exportar_reportes']
    actions_row = ["validar_reporte_fila"]
    @admin.action(description="✓ Validar reportes seleccionados")
    def validar_reportes_masivos(self, request, queryset):
        updated = queryset.update(validado=True, validado_por=request.user)
        self.message_user(request, f'{updated} reportes validados', 'success')

    @admin.action(description="📄 Exportar reportes a Excel")
    def exportar_reportes(self, request, queryset):
        # Tu lógica original de exportación...
        self.message_user(request, f'{queryset.count()} reportes exportados', 'success')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Traemos todas las llaves foráneas en un solo JOIN de SQL
        return qs.select_related("elemento", "elemento__proyecto", "cuadrilla", "reportado_por", "validado_por")

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and response.context_data.get('cl'):
            qs = response.context_data['cl'].queryset

            # Cálculos en BD para los KPIs
            kpi_total = qs.count()
            kpi_validados = qs.filter(validado=True).count()
            kpi_pendientes = qs.filter(validado=False).count()
            avg = qs.aggregate(Avg('avance_porcentaje'))['avance_porcentaje__avg'] or 0

            response.context_data.update({
                'kpi_total': kpi_total,
                'kpi_validados': kpi_validados,
                'kpi_pendientes': kpi_pendientes,
                'kpi_avg_avance': round(avg, 1),
            })
        return response

    @display(description="Elemento")
    def elemento_codigo(self, obj):
        url = reverse('admin:gestor_elementoconstructivo_change', args=[obj.elemento.pk])
        return format_html(
            '<a href="{}" class="font-semibold text-primary-600 dark:text-primary-400 hover:underline">{}</a>',
            url, obj.elemento.codigo
        )

    @display(description="Fecha de Registro", ordering="fecha")
    def fecha_hora_display(self, obj):
        return format_html(
            '<div class="flex flex-col">'
            '<span class="font-medium ">{}</span>'
            '<span class="text-xs ">{}</span>'
            '</div>',
            obj.fecha.strftime('%d/%m/%Y'),
            obj.hora.strftime('%H:%M')
        )

    @display(description="Avance Declarado", ordering="avance_porcentaje")
    def avance_display(self, obj):
        # Colores Tailwind nativos
        color_bar = "bg-emerald-500" if obj.avance_porcentaje >= 80 else (
            "bg-amber-500" if obj.avance_porcentaje >= 50 else "bg-sky-500")

        return format_html(
            '<div class="flex flex-col gap-1 min-w-[100px]">'
            '   <div class="flex justify-between items-end text-xs">'
            '       <span class="font-bold ">{}%</span>'
            '       <span class=" text-[10px]">{} ud</span>'
            '   </div>'
            '   <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">'
            '       <div class="h-1.5 rounded-full {}" style="width: {}%"></div>'
            '   </div>'
            '</div>',
            f"{obj.avance_porcentaje:,.0f}", f"{obj.avance_cantidad:,.0f}", color_bar, obj.avance_porcentaje
        )

    @display(description="Cuadrilla")
    def cuadrilla_display(self, obj):
        if obj.cuadrilla:
            return obj.cuadrilla.nombre
        return format_html('<span class="text-muted">N/A</span>')

    @display(description="Reportado Por", header=True)
    def reportado_por_display(self, obj):
        # Diseño Avatar de Unfold
        if obj.reportado_por:
            nombre = obj.reportado_por.get_full_name() or obj.reportado_por.username
            partes = nombre.split()
            iniciales = "".join(p[0] for p in partes[:2]).upper() if partes else "OP"
            return [
                nombre,
                "Supervisor de Campo",
                iniciales,
                {"path": None, "height": 24, "width": 24}
            ]
        return ["Sistema", "Automático", "SY", {"path": None, "height": 24, "width": 24}]

    @display(description="Calidad", label={"Validado": "success", "Pendiente": "warning"})
    def validado_badge(self, obj):
        # Unfold aplica el color y el badge en automático basado en el diccionario
        return "Validado" if obj.validado else "Pendiente"

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

    @display(description="Ubicación Geográfica")
    def mapa_ubicacion(self, obj):
        if not obj.latitud or not obj.longitud:
            return "Coordenadas no registradas en campo."

        # Pasamos el objeto y nombres únicos para el mapa al template
        return render_to_string(
            "admin/gestor/components/mapa_reporte.html",
            {
                "obj": obj,
                "map_id": f"map_reporte_{obj.pk}",
                "callback_name": f"initMap_{obj.pk}"
            }
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




    @action(description="Validar ✓")
    def validar_reporte_fila(self, request, object_id):
        obj = self.get_object(request, object_id)

        if obj and not obj.validado:
            obj.validado = True
            obj.validado_por = request.user
            obj.save()
            self.message_user(request, f"Reporte {obj.elemento.codigo} validado.", "success")
        elif obj and obj.validado:
            self.message_user(request, "Este reporte ya estaba validado.", "warning")

        # SOLUCIÓN: Redirigir al usuario de vuelta a la página desde la que hizo clic
        return redirect(request.META.get('HTTP_REFERER', 'admin:gestor_reporteavance_changelist'))