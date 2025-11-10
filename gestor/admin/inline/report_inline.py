from unfold.admin import TabularInline
from gestor.models import ReporteAvance

class ReporteInline(TabularInline):
    model = ReporteAvance
    extra = 0
    fields = ['fecha', 'avance_porcentaje', 'reportado_por', 'validado']
    readonly_fields = ['fecha', 'reportado_por']
    can_delete = False
    show_change_link = True
