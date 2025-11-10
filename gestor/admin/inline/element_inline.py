
from django.utils.html import format_html
from unfold.admin import TabularInline
from unfold.decorators import display

from gestor.models import ElementoConstructivo


class ElementoInline(TabularInline):
    model = ElementoConstructivo
    extra = 0
    fields = ['codigo', 'nombre', 'tipo', 'estado', 'porcentaje_avance_display']
    readonly_fields = ['porcentaje_avance_display']
    can_delete = False
    show_change_link = True

    @display(description="Avance", ordering="porcentaje_avance")
    def porcentaje_avance_display(self, obj):
        if not obj.pk:
            return "-"
        color = 'success' if obj.porcentaje_avance >= 80 else 'warning' if obj.porcentaje_avance >= 50 else 'danger'
        return format_html(
            '<span class="badge badge-{}">{:.1f}%</span>',
            color, obj.porcentaje_avance
        )
