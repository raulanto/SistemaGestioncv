from django.contrib import admin

from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from gestor.models.cuadrilla_model import Cuadrilla
from django.shortcuts import redirect
from unfold.decorators import action
from django.urls import path
from django.template.response import TemplateResponse




@admin.register(Cuadrilla)
class CuadrillaAdmin(ModelAdmin):
    list_display = [
        "nombre",
        "display_actividad",  # Qué están haciendo
        "display_integrantes",  # Quiénes son (Dropdown)
        "badge_estado",  # Semáforo de estado
    ]

    list_filter = ["proyecto"]
    search_fields = ["nombre", "proyecto__nombre", "miembros__username", "miembros__first_name"]
    # actions_list = ["ir_a_monitor_vivo"]

    @action(description="📺 Monitor en Vivo", url_path="monitor-vivo-redirect")
    def ir_a_monitor_vivo(self, request):
        # Este botón aparecerá arriba de la tabla y redirigirá a nuestra vista personalizada
        return redirect("admin:cuadrilla_monitor_vivo")

    # =========================================================
    # 2. REGISTRO DE LA NUEVA URL DENTRO DEL ADMIN
    # =========================================================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "monitor-vivo/",
                self.admin_site.admin_view(self.monitor_vivo_view),
                name="cuadrilla_monitor_vivo"
            ),
        ]
        # Ponemos custom_urls primero para que Django las evalúe antes que las de por defecto
        return custom_urls + urls

    # =========================================================
    # 3. LA LÓGICA DE LA VISTA (Zero N+1 Queries)
    # =========================================================
    def monitor_vivo_view(self, request):
        # Filtramos solo cuadrillas activas.
        # Traemos en una sola consulta toda la estructura y los trabajadores.
        cuadrillas = Cuadrilla.objects.filter(estado="ACTIVA").select_related(
            "proyecto", "elemento_actual", "lider"
        ).prefetch_related("miembros")

        # Inyectamos el contexto de Unfold para no perder el menú lateral ni el Dark Mode
        context = dict(
            self.admin_site.each_context(request),
            title="Monitor de Operaciones en Campo",
            cuadrillas=cuadrillas,
        )
        return TemplateResponse(request, "admin/gestor/cuadrilla/monitor_vivo.html", context)
    # =========================================================
    # 1. OPTIMIZACIÓN ABSOLUTA DE BASE DE DATOS (Regla de Oro)
    # =========================================================
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # select_related para llaves foráneas (1 a 1)
        # prefetch_related para la relación Muchos a Muchos (Trabajadores/Usuarios)
        return qs.select_related("proyecto", "elemento_actual").prefetch_related("miembros")

    # =========================================================
    # 2. COLUMNA: ¿QUÉ ESTÁN HACIENDO? (Contexto de Obra)
    # =========================================================
    @display(description="Actividad Actual")
    def display_actividad(self, obj):
        # Asumiendo que la cuadrilla tiene un campo 'elemento_actual' o similar
        if obj.elemento_actual:
            return format_html(
                '<div class="flex flex-col">'
                '<span class="font-bold ">{}</span>'
                '<span class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[200px]">{}</span>'
                '</div>',
                obj.elemento_actual.codigo,  # Ej: "ZAP-01"
                obj.proyecto.nombre if obj.proyecto else "Proyecto Global"
            )
        return format_html(
            '<span class="text-amber-500 dark:text-amber-400 italic font-medium">Sin asignación (En base)</span>')

    # =========================================================
    # 3. COLUMNA: ¿QUIÉNES SON? (Dropdown Interactivo)
    # =========================================================
    @display(description="Integrantes", dropdown=True)
    def display_integrantes(self, obj):
        # Gracias al prefetch_related, este .all() NO golpea la base de datos de nuevo
        miembros = obj.miembros.all()
        total = len(miembros)

        if total == 0:
            return "-"

        items = []
        for miembro in miembros:
            nombre = miembro.get_full_name() or miembro.username
            # Si tienes un perfil con el puesto (ej. "Fierrero", "Albañil"), lo llamamos aquí.
            # Si no, usamos un texto genérico o su email.
            puesto = getattr(miembro, 'puesto', 'Operativo')

            # Formato de dos líneas para el dropdown
            title = format_html(
                """
                <div class="flex flex-col overflow-hidden px-1">
                    <span class="truncate font-semibold ">{}</span>
                    <span class="truncate text-[10px]  uppercase tracking-wider">{}</span>
                </div>
                """,
                nombre,
                puesto
            )

            # Opcional: Generar link para ver el perfil del trabajador
            # link = reverse('admin:auth_user_change', args=[miembro.id])

            items.append({
                "title": title,
                # "link": link,
            })

        return {
            "title": f"{total} Trabajadores",
            "items": items,
            "striped": True,
            "max_height": 280,  # Altura perfecta para ver ~5-6 trabajadores y scrollear el resto
        }

    # =========================================================
    # 4. COLUMNA: SEMÁFORO DE ESTADO (Componente Nativo)
    # =========================================================
    @display(
        description="Estatus",
        label={
            "ACTIVA": "success",  # Verde: Trabajando en campo
            "INACTIVA": "danger",  # Rojo: Desarticulada
            "DESCANSO": "warning",  # Ámbar: Fin de turno / Pausa
        },
    )
    def badge_estado(self, obj):
        # Retornamos el valor crudo y Unfold aplica el color y el get_estado_display()
        return obj.estado