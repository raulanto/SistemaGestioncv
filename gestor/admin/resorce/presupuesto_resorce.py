from import_export import resources
from gestor.models import ConceptoPresupuesto

class ConceptoPresupuestoResource(resources.ModelResource):
    class Meta:
        model = ConceptoPresupuesto
        fields = ('id', 'proyecto', 'clave', 'descripcion', 'unidad', 'cantidad_contratada', 'precio_unitario', 'importe_contratado')
        export_order = fields
