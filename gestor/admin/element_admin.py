from django.utils.safestring import mark_safe
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeNumericFilter,
    ChoicesDropdownFilter,
    SliderNumericFilter
)
from unfold.decorators import display
from django.template.loader import render_to_string
from gestor.models import ElementoConstructivo
from .resorce import ElementoResource


@admin.register(ElementoConstructivo)
class ElementoConstructivoAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_class = ElementoResource
    list_filter_submit = True
    list_sections_classes = "lg:grid-cols-2"

    list_display = [
        'codigo',
        'nombre_corto',
        'tipo_badge',
        'proyecto_link',
        'estado_badge',
        'avance_bar',
        'responsable_display',
        'dias_programados',
    ]

    list_filter = [
        ('tipo', ChoicesDropdownFilter),
        ('estado', ChoicesDropdownFilter),
        ('proyecto', admin.RelatedOnlyFieldListFilter),
        ('porcentaje_avance', SliderNumericFilter),
        ('fecha_fin_programada', RangeDateFilter),
    ]

    search_fields = ['codigo', 'nombre', 'proyecto__codigo', 'proyecto__nombre']

    readonly_fields = [
        'utm_display',
        'coordenadas_card',
        'avance_timeline',
        'geometria_card',
    ]

    fieldsets = (
        ('Identificación', {
            'fields': ('proyecto', 'codigo', 'nombre', 'tipo'),
            'classes': ['tab'],
        }),
        ('Ubicación', {
            'fields': (
                ('latitud', 'longitud', 'elevacion'),
                'coordenadas_card',
            ),
            'classes': ['tab'],
        }),
        ('Geometría', {
            'fields': (
                ('area_proyecto', 'volumen_proyecto', 'longitud_proyecto'),
                'geometria_card',
            ),
            'classes': ['tab'],
        }),
        ('Control de Avance', {
            'fields': (
                ('estado', 'porcentaje_avance'),
                'responsable',
                'avance_timeline',
            ),
            'classes': ['tab'],
        }),
        ('Programación', {
            'fields': (
                ('fecha_inicio_programada', 'fecha_inicio_real'),
                ('fecha_fin_programada', 'fecha_fin_real'),
            ),
            'classes': ['tab'],
        }),
    )

    # list_before_template = "proyecto/list_before_template.html"
    # list_after_template = "proyecto/list_after_template.html"

    @display(description="Elemento", ordering="nombre")
    def nombre_corto(self, obj):
        nombre_display = obj.nombre[:35] + '...' if len(obj.nombre) > 35 else obj.nombre
        return format_html(
            '''
            <div class="flex flex-col gap-0.5">
                <span class="font-semibold text-sm text-base-900 dark:text-base-100">{}</span>
                <span class="text-xs text-base-500 dark:text-base-400 font-mono">{}</span>
            </div>
            ''',
            nombre_display,
            obj.codigo
        )

    # Asegúrate de tener estas importaciones al inicio de tu admin.py
    from django.utils.html import format_html
    from django.template.loader import render_to_string
    from django.contrib import admin

    # ... dentro de tu ModelAdmin ...

    @display(description="Tipo", ordering="tipo")
    def tipo_badge(self, obj):
        tipos_config = {
            'ZAPATA': {
                'color': 'primary',
            },
            'COLUMNA': {
                'color': 'warning',
            },
            'TRABE': {
                'color': 'info',
            },
            'LOSA': {
                'color': 'danger',
            },
            'MURO': {
                'color': 'warning',
            },
            'CIMENTACION': {
                'color': 'info',
            },
        }


        config = tipos_config.get(obj.tipo, {
            'color': 'primary',

        })


        context = {
            'text': obj.get_tipo_display(),
            'type': config['color'],
        }

        if 'icon' in config:
            context['icon'] = config['icon']


        html_badge = render_to_string(
            "unfold/helpers/label.html",
            context
        )

        # 6. Devolvemos el HTML seguro
        return format_html("{}", html_badge)

    @display(description="Proyecto")
    def proyecto_link(self, obj):
        url = reverse('admin:gestor_proyecto_change', args=[obj.proyecto.pk])
        return format_html(
            '''
            <a href="{}" class="inline-flex items-center gap-1.5 text-sm font-medium 
               text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 
               transition-colors duration-150">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
                {}
            </a>
            ''',
            url,
            obj.proyecto.codigo
        )

    @display(description="Estado", ordering="estado")
    def estado_badge(self, obj):
        estados_config = {
            'PENDIENTE': {
                'color': 'warning',
            },
            'REPLANTEO': {
                'color': 'danger',
            },
            'EXCAVACION': {
                'color': 'success',
            },
            'CIMBRADO': {
                'color': 'inf',
            },
            'ARMADO': {
                'color': 'success',
            },
            'COLADO': {
                'color': 'primary',
            },
            'TERMINADO': {
                'color': 'success',
            },
        }

        config = estados_config.get(obj.estado, estados_config['PENDIENTE'])

        # 1. Preparamos el contexto para el componente de Unfold
        context = {
            'text': obj.get_estado_display(),
            'type': config['color'],  # Pasamos tus clases de color personalizadas
        }

        # 2. Añadimos el ícono al contexto si existe
        if 'icon' in config:
            context['icon'] = config['icon']

        # 3. Renderizamos el componente de Unfold
        html_badge = render_to_string(
            "unfold/helpers/label.html",  # <-- El componente de Unfold
            context
        )

        # 4. Devolvemos el HTML seguro
        return format_html("{}", html_badge)

    @display(description="Avance", ordering="porcentaje_avance")
    def avance_bar(self, obj):


        if obj.porcentaje_avance is None:
            return format_html(
                '<span class="text-xs text-base-400 dark:text-base-500">N/A</span>'
            )

        porcentaje = round(obj.porcentaje_avance, 1)

        if porcentaje >= 80:
            color_class = 'bg-green-500'
        elif porcentaje >= 50:
            color_class = 'bg-yellow-500'
        elif porcentaje >= 25:
            color_class = 'bg-orange-500'
        else:
            color_class = 'bg-red-500'

        context = {
            'value': porcentaje,
            'description': f'{porcentaje}%',
            'progress_class': color_class,
        }

        html_progress = render_to_string(
            "unfold/components/progress.html",
            context
        )

        return format_html("{}", html_progress)

    @display(description="Responsable")
    def responsable_display(self, obj):

        if obj.responsable:
            # --- Caso A: Hay un responsable (Usamos el helper "avatar") ---

            # 1. Lógica de Python (la tuya era perfecta)
            nombre = obj.responsable.get_full_name() or obj.responsable.username
            iniciales = ''.join([palabra[0].upper() for palabra in nombre.split()[:2]])

            # 2. Preparamos el contexto para el helper "avatar"
            context = {
                'initials': iniciales,
                'text': obj.responsable.first_name or obj.responsable.username[:12],
                'tooltip': nombre  # Tooltip para ver el nombre completo
            }

            # 3. Renderizamos el helper "avatar.html"
            template_name = "components/avatar.html"
            html_display = render_to_string(template_name, context)

        else:
            # --- Caso B: No hay responsable (Usamos el helper "label") ---

            # 1. Preparamos el contexto para el helper "label"
            context = {
                'text': 'Sin asignar',
                # Pasamos tus clases de color personalizadas
                'type': 'bg-base-100 text-base-600 dark:bg-base-800 dark:text-base-400',
                # Reemplazamos tu SVG con el nombre del ícono de Heroicons
                'icon': 'heroicons.outline.user-circle'
            }

            # 2. Renderizamos el helper "label.html"
            template_name = "unfold/helpers/label.html"
            html_display = render_to_string(template_name, context)

        # 4. Devolvemos el HTML seguro (sea cual sea el que se haya renderizado)
        return format_html("{}", html_display)

    @display(description="Programación")
    def dias_programados(self, obj):

        if not obj.fecha_fin_programada:
            return format_html(
                '<span class="text-xs text-base-400 dark:text-base-500">Sin fecha</span>'
            )


        context = {}
        hoy = timezone.now().date()


        if obj.estado == 'TERMINADO':
            if obj.fecha_fin_real:
                diferencia = (obj.fecha_fin_real - obj.fecha_fin_programada).days

                if diferencia <= 0:
                    # Terminado a tiempo
                    context = {
                        'text': 'A tiempo',
                        'type': 'success',

                    }
                else:
                    # Terminado con retraso
                    context = {
                        'text': f'+{diferencia} días',
                        'type': 'warning',

                    }
            else:
                # Terminado pero sin fecha real (fallback)
                context = {
                    'text': 'Terminado',
                    'type': 'success',

                }

        # Caso B: El estado NO es "TERMINADO" (Calcula días restantes)
        if not context:  # Solo si no se definió en el bloque "TERMINADO"
            dias = (obj.fecha_fin_programada - hoy).days

            if dias < 0:
                # Atrasado
                context = {
                    'text': f'{abs(dias)} días atraso',
                    'type': 'danger',
                }
            elif dias < 7:
                # Urgente
                context = {
                    'text': f'{dias} días',
                    'type': 'warning',

                }
            elif dias < 30:
                # Atención
                context = {
                    'text': f'{dias} días',
                    'type': 'info',

                }
            else:
                # A tiempo
                context = {
                    'text': f'{dias} días',
                    'type': 'primary',

                }

        html_badge = render_to_string(
            "unfold/helpers/label.html",
            context
        )

        return format_html("{}", html_badge)


    @display(description="Coordenadas Geográficas")
    def utm_display(self, obj):
        if obj.utm_este and obj.utm_norte:
            return format_html(
                '''
                <div class="bg-base-50 dark:bg-base-900 rounded-lg p-3 border border-base-200 dark:border-base-700">
                    <div class="flex items-center gap-2 mb-2">
                        <svg class="w-4 h-4 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                        </svg>
                        <span class="text-xs font-semibold text-base-700 dark:text-base-300">UTM Zona {}</span>
                    </div>
                    <div class="space-y-1 font-mono text-xs">
                        <div class="flex justify-between">
                            <span class="text-base-500 dark:text-base-400">Este:</span>
                            <span class="text-base-900 dark:text-base-100 font-semibold">{} m</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-base-500 dark:text-base-400">Norte:</span>
                            <span class="text-base-900 dark:text-base-100 font-semibold">{} m</span>
                        </div>
                    </div>
                </div>
                ''',
                obj.utm_zona,
                f'{obj.utm_este:.2f}',
                f'{obj.utm_norte:.2f}'
            )
        return format_html(
            '''
            <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs 
                   bg-base-100 dark:bg-base-800 text-base-600 dark:text-base-400 border border-base-200 dark:border-base-700">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Calcular UTM
            </span>
            '''
        )


    @admin.display(description="Información de Coordenadas")
    def coordenadas_card(self, obj):

        if not obj.pk:
            return format_html(
                '<div class="p-4 rounded-lg bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-500">'
                'Guarde el elemento para ver la información de coordenadas.'
                '</div>'
            )

        # --- Manejo de valores None (El Problema Estaba Aquí) ---

        # Comprueba los valores de WGS84 ANTES de formatearlos
        lat_str = f'{obj.latitud:.6f}' if obj.latitud is not None else 'N/A'
        lon_str = f'{obj.longitud:.6f}' if obj.longitud is not None else 'N/A'
        elev_str = f'{obj.elevacion:.2f}' if obj.elevacion is not None else 'N/A'

        # Tus comprobaciones de UTM (estaban bien, solo las hice un poco más explícitas)
        utm_este_str = f'{obj.utm_este:.2f}m' if obj.utm_este is not None else 'N/A'
        utm_norte_str = f'{obj.utm_norte:.2f}m' if obj.utm_norte is not None else 'N/A'
        utm_zona_str = str(obj.utm_zona) if obj.utm_zona is not None else 'N/A'

        # --- Renderizado de HTML ---

        # El HTML de tu plantilla (sin cambios)
        html_template = '''
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-base-50 dark:bg-base-900 rounded-lg">
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4">
                    <div class="flex items-center gap-2 mb-3 pb-3 border-b border-base-200 dark:border-base-700">
                        <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                             <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">

<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>

</svg> </div>
                        <span class="text-sm font-semibold text-base-900 dark:text-base-100">WGS84</span>
                    </div>
                    <div class="space-y-2 font-mono text-xs">
                        <div class="flex justify-between items-center">
                            <span class="text-base-500 dark:text-base-400">Latitud:</span>
                            <span class="text-base-900 dark:text-base-100 font-semibold">{}°</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-base-500 dark:text-base-400">Longitud:</span>
                            <span class="text-base-900 dark:text-base-100 font-semibold">{}°</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-base-500 dark:text-base-400">Elevación:</span>
                            <span class="text-base-900 dark:text-base-100 font-semibold">{} m</span>
                        </div>
                    </div>
                </div>

                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4">
                    <div class="flex items-center gap-2 mb-3 pb-3 border-b border-base-200 dark:border-base-700">
                        <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                            <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">

<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>

</svg>  </div>
                        <span class="text-sm font-semibold text-base-900 dark:text-base-100">UTM</span>
                    </div>
                    <div class="space-y-2 font-mono text-xs">
                        <div class="flex justify-between items-center">
                            <span class="text-base-500 dark:text-base-400">Este:</span>
                            <span class="text-base-900 dark:text-base-100 font-semibold">{}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-base-500 dark:text-base-400">Norte:</span>
                            <span class="text-base-900 dark:text-base-100 font-semibold">{}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-base-500 dark:text-base-400">Zona:</span>
                            <span class="text-base-900 dark:text-base-100 font-semibold">{}</span>
                        </div>
                    </div>
                </div>
            </div>
            '''

        return format_html(
            html_template,
            lat_str,
            lon_str,
            elev_str,
            utm_este_str,
            utm_norte_str,
            utm_zona_str
        )

    @display(description="Información de Geometría")
    def geometria_card(self, obj):
        area_str = f'{obj.area_proyecto:.2f} m²' if obj.area_proyecto else 'N/A'
        volumen_str = f'{obj.volumen_proyecto:.2f} m³' if obj.volumen_proyecto else 'N/A'
        longitud_str = f'{obj.longitud_proyecto:.2f} m' if obj.longitud_proyecto else 'N/A'

        return format_html(
            '''
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 bg-base-50 dark:bg-base-900 rounded-lg">

                <!-- Área -->
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4 text-center">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-purple-100 dark:bg-purple-900/30 mb-3">
                        <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"/>
                        </svg>
                    </div>
                    <div class="text-xl font-bold text-base-900 dark:text-base-100 mb-1">{}</div>
                    <div class="text-xs text-base-500 dark:text-base-400 uppercase tracking-wide">Área</div>
                </div>

                <!-- Volumen -->
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4 text-center">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900/30 mb-3">
                        <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                        </svg>
                    </div>
                    <div class="text-xl font-bold text-base-900 dark:text-base-100 mb-1">{}</div>
                    <div class="text-xs text-base-500 dark:text-base-400 uppercase tracking-wide">Volumen</div>
                </div>

                <!-- Longitud -->
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4 text-center">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-green-100 dark:bg-green-900/30 mb-3">
                        <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                        </svg>
                    </div>
                    <div class="text-xl font-bold text-base-900 dark:text-base-100 mb-1">{}</div>
                    <div class="text-xs text-base-500 dark:text-base-400 uppercase tracking-wide">Longitud</div>
                </div>

            </div>
            ''',
            area_str,
            volumen_str,
            longitud_str
        )

    @display(description="Historial de Avance")
    def avance_timeline(self, obj):
        if not obj.pk:
            return format_html(
                '<div class="text-sm text-base-500 dark:text-base-400">Guarde el elemento para ver el historial</div>'
            )

        reportes = obj.reportes.order_by('-created_at')[:5]

        if not reportes:
            return format_html(
                '''
                <div class="flex flex-col items-center justify-center p-8 bg-base-50 dark:bg-base-900 rounded-lg border-2 border-dashed border-base-300 dark:border-base-700">
                    <svg class="w-12 h-12 text-base-400 dark:text-base-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    <p class="text-sm font-medium text-base-600 dark:text-base-400">Sin reportes de avance</p>
                    <p class="text-xs text-base-500 dark:text-base-500 mt-1">Los reportes aparecerán aquí</p>
                </div>
                '''
            )

        timeline_html = '''
            <div class="bg-base-50 dark:bg-base-900 rounded-lg p-4">
                <div class="space-y-4 relative">
        '''

        for i, reporte in enumerate(reportes):
            avance_str = f'{reporte.avance_porcentaje:.1f}'
            desc_corta = reporte.descripcion[:60] + '...' if len(reporte.descripcion) > 60 else reporte.descripcion
            fecha_str = reporte.fecha.strftime('%d %b %Y') if hasattr(reporte,
                                                                      'fecha') else reporte.created_at.strftime(
                '%d %b %Y')

            # Determinar color del punto según avance
            if reporte.avance_porcentaje >= 80:
                point_color = 'bg-green-500'
                line_color = 'border-green-500'
            elif reporte.avance_porcentaje >= 50:
                point_color = 'bg-yellow-500'
                line_color = 'border-yellow-500'
            else:
                point_color = 'bg-orange-500'
                line_color = 'border-orange-500'

            # Agregar línea excepto en el último elemento
            line_html = '' if i == len(reportes) - 1 else f'''
                <div class="absolute left-[15px] top-8 bottom-0 w-0.5 {line_color} border-l-2 border-dashed"></div>
            '''

            timeline_html += f'''
                <div class="relative pl-10">
                    <div class="absolute left-0 top-1 w-8 h-8 {point_color} rounded-full border-4 border-white dark:border-base-800 shadow-md flex items-center justify-center">
                        <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                    {line_html}
                    <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-3">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-medium text-base-500 dark:text-base-400">{fecha_str}</span>
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-400">
                                {avance_str}%
                            </span>
                        </div>
                        <p class="text-sm text-base-700 dark:text-base-300">{desc_corta}</p>
                        {f'<div class="text-xs text-base-500 dark:text-base-400 mt-1">Por: {reporte.reportado_por.get_full_name() or reporte.reportado_por.username}</div>' if hasattr(reporte, 'reportado_por') and reporte.reportado_por else ''}
                    </div>
                </div>
            '''

        timeline_html += '''
                </div>
            </div>
        '''

        return mark_safe(timeline_html)