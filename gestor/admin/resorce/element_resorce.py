from gestor.models import ElementoConstructivo
from import_export import resources, fields

class ElementoResource(resources.ModelResource):
    proyecto_codigo = fields.Field(
        column_name='proyecto_codigo',
        attribute='proyecto__codigo'
    )

    class Meta:
        model = ElementoConstructivo
        fields = ('codigo', 'nombre', 'tipo', 'proyecto_codigo', 'latitud',
                  'longitud', 'estado', 'porcentaje_avance')

