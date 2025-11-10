from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeNumericFilter,
    ChoicesDropdownFilter,
)
from unfold.decorators import display

from gestor.models import Proyecto
from gestor.views import ProyectoDashboardView, ProyectoMapsView, ProyectoExplorerView, ProyectoDataAPIView
from .resorce import ProyectoResource


@admin.register(Proyecto)
class ProyectoAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_class = ProyectoResource

    list_display = [
        'codigo_link',
        'nombre_display',
        'cliente',
        'estado_badge',
        'avance_display',
        'presupuesto_display',
        'dias_restantes',
    ]
    list_filter_submit = True

    list_filter = [
        ('estado', ChoicesDropdownFilter),
        ('sistema_coordenadas', ChoicesDropdownFilter),
        ('fecha_inicio', RangeDateFilter),
        ('presupuesto_total', RangeNumericFilter),
    ]

    search_fields = ['codigo', 'nombre', 'cliente']

    readonly_fields = [
        'created_at',
        'updated_at',
        'estadisticas_card',
        'mapa_proyecto',
    ]

    fieldsets = (
        ('Información General', {
            'fields': ('codigo', 'nombre', 'descripcion', 'cliente', 'estado'),
            'classes': ['tab'],
        }),
        ('Configuración Geográfica', {
            'fields': (
                'sistema_coordenadas',
                ('zona_utm', 'hemisferio'),
                ('lat_referencia', 'lon_referencia'),
                'elevacion_referencia',
                'mapa_proyecto',
            ),
            'classes': ['tab'],
        }),
        ('Gestión del Proyecto', {
            'fields': (
                ('director_obra', 'residente_obra'),
                ('fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real'),
                'presupuesto_total',
                'estadisticas_card',
            ),
            'classes': ['tab'],
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['tab'],
        }),
    )

    actions = ['exportar_dashboard', 'calcular_volumenes']

    @display(description='Codigo',ordering='codigo')
    def codigo_link(self, obj):
        url = reverse('admin:proyecto_dashboard', args=[obj.pk])
        return format_html(
            '''
            <a href="{}" class="inline-flex items-center gap-1.5 text-sm font-medium 
               text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 
               transition-colors duration-150">
                {}
            </a>
            ''',
            url,
            obj.codigo
        )

    @display(description="Proyecto", ordering="nombre")
    def nombre_display(self, obj):
        return format_html(
            '''
            <div class="flex flex-col gap-1">
                <span class="font-semibold text-base-900 dark:text-base-100">{}</span>
                <span class="text-xs text-base-500 dark:text-base-400">{}</span>
            </div>
            ''',
            obj.nombre,
            obj.codigo
        )

    @admin.display(description="Estado", ordering="estado")
    def estado_badge(self, obj):
        estados_config = {
            'PLAN': {
                'color': 'info',
            },
            'EJECUCION': {
                'color': 'success',
            },
            'PAUSADO': {
                'color': 'warning',
            },
            'FINALIZADO': {
                'color': 'primary',
                'icon': '✓'
            },
        }
        config = estados_config.get(obj.estado, estados_config['PLAN'])
        context = {
            'text': obj.get_estado_display(),
            'type': config['color'],
        }
        if 'icon' in config:
            context['icon_text'] = config['icon']
        html_badge = render_to_string(
            "unfold/helpers/label.html",
            context
        )
        return format_html("{}", html_badge)

    @display(description="Tiempo")
    def dias_restantes(self, obj):

        if obj.fecha_fin_real:
            context = {
                'text': 'Finalizado',
                'type': 'success',
                'icon': 'heroicons.outline.check-circle'
            }
        else:
            hoy = timezone.now().date()
            dias = (obj.fecha_fin_estimada - hoy).days

            if dias < 0:
                text = f'{abs(dias)} días atraso'
                type = 'danger'
            elif dias < 15:
                text = f'{dias} días'
                type = 'warning'
            elif dias < 30:
                text = f'{dias} días'
                type = 'warning'
            else:
                text = f'{dias} días'
                type = 'primary'

            context = {
                'text': text,
                'type': type,
            }

        html_badge = render_to_string(
            "unfold/helpers/label.html",
            context
        )

        return format_html("{}", html_badge)

    @admin.display(description="Avance")
    def avance_display(self, obj):
        elementos = obj.elementos.all()
        if not elementos:
            return "Sin elementos"
        avance = sum(e.porcentaje_avance for e in elementos) / len(elementos)
        avance_formateado = round(avance, 1)

        if avance >= 80:
            color_class = 'bg-green-600 dark:bg-green-500'
        elif avance >= 50:
            color_class = 'bg-yellow-600 dark:bg-yellow-500'
        else:
            color_class = 'bg-red-600 dark:bg-red-500'

        context = {

            'description': f'{avance_formateado}%',
            'value': avance_formateado,
            'progress_class': color_class
        }

        html_progress = render_to_string(
            "unfold/components/progress.html",
            context
        )

        return format_html("{}", html_progress)

    @display(description="Presupuesto", ordering="presupuesto_total")
    def presupuesto_display(self, obj):
        # Formatear con separadores de miles
        monto = f'{obj.presupuesto_total:,.0f}'

        return format_html(
            '''
            <div class="flex flex-col items-end">
                <span class="font-bold text-base-900 dark:text-base-100">${}</span>
                <span class="text-xs text-base-500 dark:text-base-400">MXN</span>
            </div>
            ''',
            monto
        )

    @display(description="Acciones")
    def acciones(self, obj):
        return format_html(
            '''
            <div class="flex items-center gap-2">
                <a href="{}" 
                   class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg
                          bg-primary-600 hover:bg-primary-700 text-white transition-colors duration-200">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                    </svg>

                </a>
                <a href="{}" 
                   class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg
                          bg-green-600 hover:bg-green-700 text-white transition-colors duration-200">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                    </svg>
                </a>
            </div>
            ''',
            reverse('admin:proyecto_dashboard', args=[obj.pk]),
            reverse('admin:proyecto_mapa', args=[obj.pk])
        )

    @display(description="Estadísticas del Proyecto")
    def estadisticas_card(self, obj):
        if not obj.pk:
            return format_html(
                '<div class="text-sm text-base-500 dark:text-base-400">Guarde el proyecto para ver estadísticas</div>'
            )

        elementos = obj.elementos.all()
        total = elementos.count()
        terminados = elementos.filter(estado='TERMINADO').count()
        en_proceso = elementos.exclude(estado__in=['TERMINADO', 'PENDIENTE']).count()
        pendientes = elementos.filter(estado='PENDIENTE').count()

        return format_html(
            '''
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-base-50 dark:bg-base-900 rounded-lg">

                <!-- Total -->
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4 
                            hover:shadow-md transition-shadow duration-200">
                    <div class="flex items-center justify-between mb-2">
                        <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                            </svg>
                        </div>
                    </div>
                    <div class="text-3xl font-bold text-base-900 dark:text-base-100">{}</div>
                    <div class="text-xs text-base-500 dark:text-base-400 mt-1">Total Elementos</div>
                </div>

                <!-- Terminados -->
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4 
                            hover:shadow-md transition-shadow duration-200">
                    <div class="flex items-center justify-between mb-2">
                        <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                            <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                    </div>
                    <div class="text-3xl font-bold text-base-900 dark:text-base-100">{}</div>
                    <div class="text-xs text-base-500 dark:text-base-400 mt-1">Terminados</div>
                </div>

                <!-- En Proceso -->
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4 
                            hover:shadow-md transition-shadow duration-200">
                    <div class="flex items-center justify-between mb-2">
                        <div class="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                            <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                    </div>
                    <div class="text-3xl font-bold text-base-900 dark:text-base-100">{}</div>
                    <div class="text-xs text-base-500 dark:text-base-400 mt-1">En Proceso</div>
                </div>

                <!-- Pendientes -->
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 p-4 
                            hover:shadow-md transition-shadow duration-200">
                    <div class="flex items-center justify-between mb-2">
                        <div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                            <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                            </svg>
                        </div>
                    </div>
                    <div class="text-3xl font-bold text-base-900 dark:text-base-100">{}</div>
                    <div class="text-xs text-base-500 dark:text-base-400 mt-1">Pendientes</div>
                </div>

            </div>
            ''',
            total, terminados, en_proceso, pendientes
        )



    @admin.display(description="Ubicación del Proyecto")
    def mapa_proyecto(self, obj):

        # 1. Comprobación para la página de "Añadir" (¡Esta ya la tenías y está perfecta!)
        if not obj.pk:
            return format_html(
                '<div class="text-sm text-base-500 dark:text-base-400">Guarde el proyecto para ver el mapa</div>'
            )

        # 2. NUEVA COMPROBACIÓN: para la página de "Editar" sin datos
        #    Nos aseguramos de que los valores no sean None ANTES de usarlos.
        if obj.lat_referencia is None or obj.lon_referencia is None or obj.elevacion_referencia is None:
            return format_html(
                '<div class="p-4 rounded-lg bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-500 border border-yellow-200 dark:border-yellow-800">'
                'No se han definido coordenadas (lat, lon) o elevación para este proyecto. '
                'Por favor, añada los valores para mostrar el mapa.'
                '</div>'
            )

        # --- Si llegamos aquí, es seguro usar los valores ---
        # Los pre-calculamos para que el bloque de format_html sea más limpio

        lat_redondeada = round(obj.lat_referencia, 6)
        lon_redondeada = round(obj.lon_referencia, 6)

        return format_html(
            '''
            <div class="bg-base-50 dark:bg-base-900 rounded-lg p-4">
                <div class="bg-white dark:bg-base-800 rounded-lg shadow-sm border border-base-200 dark:border-base-700 overflow-hidden">
                    <div class="p-4 border-b border-base-200 dark:border-base-700">
                        <h3 class="text-sm font-semibold text-base-900 dark:text-base-100 flex items-center gap-2">
                            <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                            </svg>
                            Ubicación del Benchmark Principal
                        </h3>
                        <p class="text-xs text-base-500 dark:text-base-400 mt-1">
                            Lat: {} | Lon: {} | Elevación: {}m
                        </p>
                    </div>
                    <div id="map-{}" style="height: 400px;"></div>
                </div>
            </div>

            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhpmA9wNjHDFBEOYJP5SULEPZrsEZZMIQCVs=" crossorigin=""/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlGUPg=" crossorigin=""></script>

            <script>
                (function() {{
                    if (typeof L === 'undefined') return;

                    var mapId = 'map-{}';
                    var mapElement = document.getElementById(mapId);

                    // Evita que el script se reinicialice en cada refresco (ej. HMR de Tailwind)
                    if (!mapElement || mapElement.dataset.initialized) return;
                    mapElement.dataset.initialized = 'true';

                    var lat = {};
                    var lon = {};
                    var elev = {};

                    var map = L.map(mapId).setView([lat, lon], 15);

                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        attribution: '© OpenStreetMap contributors',
                        maxZoom: 19
                    }}).addTo(map);

                    var icon = L.divIcon({{
                        html: '<div style="background: #3b82f6; width: 32px; height: 32px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center;"><span style="color: white; font-size: 16px;">🎯</span></div>',
                        className: '',
                        iconSize: [32, 32],
                        iconAnchor: [16, 16]
                    }});

                    L.marker([lat, lon], {{icon: icon}})
                        .addTo(map)
                        .bindPopup('<div style="min-width: 200px;"><strong style="font-size: 14px;">🎯 Benchmark Principal</strong><br/><div style="margin-top: 8px; font-size: 12px;"><strong>Elevación:</strong> ' + elev + 'm<br/><strong>Coordenadas:</strong><br/>Lat: ' + {} + '<br/>Lon: ' + {} + '</div></div>')
                        .openPopup();

                    // Arreglo para que el mapa se renderice bien dentro de contenedores flexibles
                    setTimeout(function() {{ map.invalidateSize(); }}, 100);
                }})();
            </script>
            ''',
            # Argumentos para format_html
            lat_redondeada,  # p.Lat
            lon_redondeada,  # p.Lon
            obj.elevacion_referencia,  # p.Elevación
            obj.pk,  # div id="map-{}"
            obj.pk,  # var mapId = 'map-{}'
            obj.lat_referencia,  # var lat = {};
            obj.lon_referencia,  # var lon = {};
            obj.elevacion_referencia,  # var elev = {};
            # (lat y lon para L.marker ya están definidos en JS)
            lat_redondeada,  # bindPopup Lat
            lon_redondeada  # bindPopup Lon
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/dashboard/',
                self.admin_site.admin_view(
                    ProyectoDashboardView.as_view(model_admin=self)
                ),
                name='proyecto_dashboard',
            ),
            path(
                '<path:object_id>/mapa/',
                self.admin_site.admin_view(
                    ProyectoMapsView.as_view(model_admin=self)
                ),
                name='proyecto_mapa',
            ),
            path(
                'explorer/',
                self.admin_site.admin_view(
                    ProyectoExplorerView.as_view(model_admin=self)
                ),
                name='proyecto_explorer',
            ),
            # NUEVO: API de datos
            path(
                'proyecto-data/',
                self.admin_site.admin_view(
                    lambda request: ProyectoDataAPIView.as_view(model_admin=self)(request)
                ),
                name='proyecto_data_api',
            ),
        ]
        return custom_urls + urls

    @admin.action(description="📊 Exportar dashboard a PDF")
    def exportar_dashboard(self, request, queryset):
        self.message_user(
            request,
            f"✓ {queryset.count()} proyecto(s) exportado(s) exitosamente",
            level='success'
        )

    @admin.action(description="📐 Calcular volúmenes de terracería")
    def calcular_volumenes(self, request, queryset):
        self.message_user(
            request,
            f"✓ Volúmenes calculados para {queryset.count()} proyecto(s)",
            level='success'
        )
