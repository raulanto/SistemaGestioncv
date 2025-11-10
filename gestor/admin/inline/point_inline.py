from unfold.admin import TabularInline

from gestor.models import PuntoControl


class PuntoControlInline(TabularInline):
    model = PuntoControl
    extra = 0
    fields = ['numero_punto', 'tipo', 'equipo_medicion', 'validado']
    readonly_fields = []
    can_delete = True
