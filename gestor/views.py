from datetime import timedelta
from django.views.generic import TemplateView
import json
from django.contrib.admin import AdminSite
from django.utils import timezone
from django.http import JsonResponse
from gestor.models import (Proyecto, ElementoConstructivo, ReporteAvance,PuntoControl,Cuadrilla)
from django.db.models import Avg, Count, Sum, Q
from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin
from django.db.models import Avg
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from django.contrib.admin import site as admin_site
from django.core.exceptions import PermissionDenied
from gestor.models import Proyecto
from django.utils.translation import gettext_lazy as _

class ProyectoDashboardView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Dashboard del Proyecto"  # Título que aparece en el header
    permission_required = ()  # Puedes agregar permisos aquí, ej: ("gestor.view_proyecto",)
    template_name = "board/proyecto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el proyecto usando el object_id de la URL
        proyecto = self.model_admin.get_object(
            self.request,
            self.kwargs.get('object_id')
        )

        if proyecto:
            elementos = proyecto.elementos.all()

            context.update({
                'proyecto': proyecto,
                'total_elementos': elementos.count(),
                'terminados': elementos.filter(estado='TERMINADO').count(),
                'en_proceso': elementos.exclude(
                    estado__in=['TERMINADO', 'PENDIENTE']
                ).count(),
                'pendientes':elementos.exclude(
                    estado__in=['TERMINADO']
                ).count(),
                'avance_promedio': elementos.aggregate(
                    Avg('porcentaje_avance')
                )['porcentaje_avance__avg'] or 0,
                'reportes_ultima_semana': 0,
            })

        return context


class ProyectoMapsView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Dashboard del Proyecto"
    permission_required = ()
    template_name = "board/proyecto_mapa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proyecto = self.model_admin.get_object(
            self.request,
            self.kwargs.get('object_id')
        )
        if proyecto:
            elementos = proyecto.elementos.all()
            elementos_json = []
            for elemento in elementos:
                elementos_json.append({
                    'id': str(elemento.id),
                    'codigo': elemento.codigo,
                    'nombre': elemento.nombre,
                    'latitud': elemento.latitud,
                    'longitud': elemento.longitud,
                    'estado': elemento.estado,
                    'estado_display': elemento.get_estado_display(),
                    'porcentaje_avance': float(round(elemento.porcentaje_avance,2)),
                })

            context.update({
                'proyecto': proyecto,
                'elementos': elementos,
                'elementos_json': json.dumps(elementos_json),  # JSON para JavaScript
            })

        return context


def dashboard_callback(request, context):
    """
    Dashboard con estadísticas completas del sistema
    """
    # ============ ESTADÍSTICAS GENERALES ============
    total_proyectos = Proyecto.objects.count()
    proyectos_activos = Proyecto.objects.filter(estado='EJECUCION').count()
    proyectos_pausados = Proyecto.objects.filter(estado='PAUSADO').count()
    proyectos_finalizados = Proyecto.objects.filter(estado='FINALIZADO').count()

    total_elementos = ElementoConstructivo.objects.count()
    elementos_terminados = ElementoConstructivo.objects.filter(estado='TERMINADO').count()
    elementos_proceso = ElementoConstructivo.objects.exclude(
        estado__in=['TERMINADO', 'PENDIENTE']
    ).count()
    elementos_pendientes = ElementoConstructivo.objects.filter(estado='PENDIENTE').count()

    # Porcentaje de avance general
    avance_general = ElementoConstructivo.objects.aggregate(
        Avg('porcentaje_avance')
    )['porcentaje_avance__avg'] or 0

    # ============ CUADRILLAS ============
    total_cuadrillas = Cuadrilla.objects.count()
    cuadrillas_activas = Cuadrilla.objects.filter(activa=True).count()

    # ============ REPORTES ============
    hace_semana = timezone.now() - timedelta(days=7)
    hace_mes = timezone.now() - timedelta(days=30)

    reportes_semana = ReporteAvance.objects.filter(
        created_at__gte=hace_semana
    ).count()
    reportes_mes = ReporteAvance.objects.filter(
        created_at__gte=hace_mes
    ).count()
    reportes_pendientes_validacion = ReporteAvance.objects.filter(
        validado=False
    ).count()

    # ============ PUNTOS DE CONTROL ============
    puntos_control_total = PuntoControl.objects.count()
    puntos_sin_validar = PuntoControl.objects.filter(validado=False).count()

    # ============ PROYECTOS RECIENTES ============
    proyectos_recientes = Proyecto.objects.select_related(
        'director_obra', 'residente_obra'
    ).order_by('-created_at')[:5]

    # ============ PROYECTOS CON ATRASO ============
    hoy = timezone.now().date()
    proyectos_atrasados = Proyecto.objects.filter(
        estado='EJECUCION',
        fecha_fin_estimada__lt=hoy
    ).order_by('fecha_fin_estimada')[:5]

    # ============ ELEMENTOS CRÍTICOS ============
    # Elementos con bajo avance pero fecha próxima
    elementos_criticos = ElementoConstructivo.objects.filter(
        estado__in=['PENDIENTE', 'REPLANTEO', 'EXCAVACION'],
        porcentaje_avance__lt=30,
        fecha_fin_programada__lte=hoy + timedelta(days=15)
    ).select_related('proyecto', 'responsable').order_by('fecha_fin_programada')[:10]

    # ============ REPORTES RECIENTES ============
    reportes_recientes = ReporteAvance.objects.select_related(
        'elemento', 'elemento__proyecto', 'cuadrilla', 'reportado_por'
    ).order_by('-created_at')[:8]

    # ============ AVANCE POR PROYECTO ============
    proyectos_con_avance = Proyecto.objects.filter(
        estado='EJECUCION'
    ).annotate(
        avance=Avg('elementos__porcentaje_avance'),
        total_elementos=Count('elementos')
    ).order_by('-avance')[:10]

    # ============ DISTRIBUCIÓN DE ESTADOS ============
    distribucion_estados = ElementoConstructivo.objects.values(
        'estado'
    ).annotate(
        total=Count('id')
    ).order_by('-total')

    # ============ ACTIVIDAD SEMANAL (últimos 7 días) ============
    actividad_semanal = []
    for i in range(6, -1, -1):
        dia = timezone.now().date() - timedelta(days=i)
        reportes_dia = ReporteAvance.objects.filter(
            fecha=dia
        ).count()
        actividad_semanal.append({
            'dia': dia.strftime('%a'),
            'fecha': dia,
            'reportes': reportes_dia
        })

    # ============ TOP USUARIOS ACTIVOS ============
    usuarios_activos = ReporteAvance.objects.filter(
        created_at__gte=hace_mes
    ).values(
        'reportado_por__username',
        'reportado_por__first_name',
        'reportado_por__last_name'
    ).annotate(
        total_reportes=Count('id')
    ).order_by('-total_reportes')[:5]

    # ============ PRESUPUESTO TOTAL ============
    presupuesto_total = Proyecto.objects.filter(
        estado__in=['EJECUCION', 'PAUSADO']
    ).aggregate(
        total=Sum('presupuesto_total')
    )['total'] or 0

    context.update({
        # Generales
        'total_proyectos': total_proyectos,
        'proyectos_activos': proyectos_activos,
        'proyectos_pausados': proyectos_pausados,
        'proyectos_finalizados': proyectos_finalizados,

        # Elementos
        'total_elementos': total_elementos,
        'elementos_terminados': elementos_terminados,
        'elementos_proceso': elementos_proceso,
        'elementos_pendientes': elementos_pendientes,
        'avance_general': round(avance_general, 1),

        # Cuadrillas
        'total_cuadrillas': total_cuadrillas,
        'cuadrillas_activas': cuadrillas_activas,

        # Reportes
        'reportes_semana': reportes_semana,
        'reportes_mes': reportes_mes,
        'reportes_pendientes_validacion': reportes_pendientes_validacion,

        # Puntos de control
        'puntos_control_total': puntos_control_total,
        'puntos_sin_validar': puntos_sin_validar,

        # Presupuesto
        'presupuesto_total': presupuesto_total,

        # Listas
        'proyectos_recientes': proyectos_recientes,
        'proyectos_atrasados': proyectos_atrasados,
        'elementos_criticos': elementos_criticos,
        'reportes_recientes': reportes_recientes,
        'proyectos_con_avance': proyectos_con_avance,
        'distribucion_estados': distribucion_estados,
        'actividad_semanal': actividad_semanal,
        'usuarios_activos': usuarios_activos,
    })

    return context


class ProyectoExplorerView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Explorador de Proyectos"
    permission_required = ()
    template_name = "board/board_explore.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todos los proyectos con sus elementos
        proyectos = Proyecto.objects.prefetch_related(
            'elementos',
            'elementos__reportes',
            'cuadrillas'
        ).all()

        # Construir árbol de proyectos
        proyectos_tree = []
        for proyecto in proyectos:
            elementos = proyecto.elementos.all()
            proyecto_data = {
                'id': str(proyecto.id),
                'codigo': proyecto.codigo,
                'nombre': proyecto.nombre,
                'estado': proyecto.estado,
                'elementos_count': elementos.count(),
                'elementos': []
            }

            # Agregar elementos al árbol
            for elemento in elementos:
                reportes = elemento.reportes.all()
                elemento_data = {
                    'id': str(elemento.id),
                    'codigo': elemento.codigo,
                    'nombre': elemento.nombre,
                    'tipo': elemento.tipo,
                    'estado': elemento.estado,
                    'avance': float(elemento.porcentaje_avance),
                    'reportes_count': reportes.count(),
                }
                proyecto_data['elementos'].append(elemento_data)

            proyectos_tree.append(proyecto_data)

        context.update({
            'proyectos_tree': proyectos_tree,
            'proyectos_tree_json': json.dumps(proyectos_tree),
        })

        return context




# API endpoint para obtener datos del proyecto
class ProyectoDataAPIView(UnfoldModelAdminViewMixin, TemplateView):
    """API para obtener datos de un proyecto específico"""
    permission_required = ()
    def get(self, request, *args, **kwargs):
        proyecto_id = request.GET.get('proyecto_id')

        if not proyecto_id:
            return JsonResponse({'error': 'proyecto_id requerido'}, status=400)

        try:
            proyecto = Proyecto.objects.get(id=proyecto_id)
            elementos = proyecto.elementos.all()

            # KPIs
            total_elementos = elementos.count()
            terminados = elementos.filter(estado='TERMINADO').count()
            en_proceso = elementos.exclude(estado__in=['TERMINADO', 'PENDIENTE']).count()
            pendientes = elementos.filter(estado='PENDIENTE').count()
            avance_promedio = elementos.aggregate(Avg('porcentaje_avance'))['porcentaje_avance__avg'] or 0

            # Distribución de estados
            distribucion = elementos.values('estado').annotate(
                count=Count('id')
            ).order_by('-count')

            # Elementos para el mapa
            elementos_mapa = []
            for elemento in elementos:
                elementos_mapa.append({
                    'id': str(elemento.id),
                    'codigo': elemento.codigo,
                    'nombre': elemento.nombre,
                    'latitud': float(elemento.latitud),
                    'longitud': float(elemento.longitud),
                    'elevacion': float(elemento.elevacion),
                    'estado': elemento.estado,
                    'estado_display': elemento.get_estado_display(),
                    'avance': float(elemento.porcentaje_avance),
                    'tipo': elemento.tipo,
                    'tipo_display': elemento.get_tipo_display(),
                })

            # Datos del proyecto
            data = {
                'proyecto': {
                    'id': str(proyecto.id),
                    'codigo': proyecto.codigo,
                    'nombre': proyecto.nombre,
                    'cliente': proyecto.cliente,
                    'estado': proyecto.estado,
                    'estado_display': proyecto.get_estado_display(),
                    'lat_referencia': float(proyecto.lat_referencia),
                    'lon_referencia': float(proyecto.lon_referencia),
                    'elevacion_referencia': float(proyecto.elevacion_referencia),
                    'presupuesto': float(proyecto.presupuesto_total),
                    'fecha_inicio': proyecto.fecha_inicio.isoformat(),
                    'fecha_fin': proyecto.fecha_fin_estimada.isoformat(),
                },
                'kpis': {
                    'total_elementos': total_elementos,
                    'terminados': terminados,
                    'en_proceso': en_proceso,
                    'pendientes': pendientes,
                    'avance_promedio': round(avance_promedio, 1),
                },
                'distribucion_estados': list(distribucion),
                'elementos_mapa': elementos_mapa,
            }

            return JsonResponse(data)

        except Proyecto.DoesNotExist:
            return JsonResponse({'error': 'Proyecto no encontrado'}, status=404)


def admin_password_change_guard(request):
    """
    Esta vista intercepta la URL de cambio de contraseña.
    Solo deja pasar a los superusuarios.
    """
    if not request.user.is_superuser:
        # Si no es superadmin, le negamos el acceso
        raise PermissionDenied(_("Solo los superusuarios pueden cambiar contraseñas desde el admin."))

    # Si es superadmin, lo dejamos pasar a la vista de admin real
    return admin_site.password_change(request)