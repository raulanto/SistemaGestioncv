import uuid

from django.contrib.auth.models import User
from django.db import models

from .element_model import ElementoConstructivo
from .project_model import Proyecto

from .audited_model import AuditedModel
class TiposPuntoControl(models.TextChoices):
    BENCHMARK = 'BENCHMARK', 'Banco de Nivel'
    REPLANTEO = 'REPLANTEO', 'Punto de Replanteo'
    VERIFICACION = 'VERIFICACION', 'Verificación'
    CONTROL = 'CONTROL', 'Control de Calidad'
    LEVANTAMIENTO = 'LEVANTAMIENTO', 'Levantamiento'

class EquiposMedicion(models.TextChoices):
    GPS_DIFERENCIAL = 'GPS_DIFERENCIAL', 'GPS Diferencial'
    GPS_RTK = 'GPS_RTK', 'GPS RTK'
    ESTACION_TOTAL = 'ESTACION_TOTAL', 'Estación Total'
    NIVEL = 'NIVEL', 'Nivel Óptico'
    GPS_MOVIL = 'GPS_MOVIL', 'GPS Móvil'


class PuntoControl(AuditedModel):
    """
    Puntos de control topográfico y levantamientos
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='puntos_control')
    elemento = models.ForeignKey(
        ElementoConstructivo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='puntos_control'
    )

    # Identificación
    numero_punto = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)


    tipo = models.CharField(max_length=20, choices=TiposPuntoControl)

    # Coordenadas medidas
    latitud = models.FloatField()
    longitud = models.FloatField()
    elevacion = models.FloatField()

    # Precisión de la medición
    precision_horizontal = models.FloatField(
        help_text="Precisión horizontal en cm",
        null=True,
        blank=True
    )
    precision_vertical = models.FloatField(
        help_text="Precisión vertical en cm",
        null=True,
        blank=True
    )


    equipo_medicion = models.CharField(max_length=30, choices=EquiposMedicion)

    # Responsable de la medición
    topografo = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_medicion = models.DateTimeField(auto_now_add=True)

    # Validación
    validado = models.BooleanField(default=False)
    validado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='puntos_validados'
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True)

    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Punto de Control"
        verbose_name_plural = "Puntos de Control"
        ordering = ['-fecha_medicion']

    def __str__(self):
        return f"Punto {self.numero_punto} - {self.tipo}"
