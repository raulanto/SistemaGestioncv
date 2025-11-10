from import_export import resources

from gestor.models import Proyecto


class ProyectoResource(resources.ModelResource):
    class Meta:
        model = Proyecto
        fields = ('codigo', 'nombre', 'cliente', 'estado', 'fecha_inicio',
                  'fecha_fin_estimada', 'presupuesto_total')
        export_order = fields
