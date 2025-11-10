from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from .audited_model import AuditedModel
from .project_model import Proyecto


class TiposElemento(models.TextChoices):
    ZAPATA = 'ZAPATA', 'Zapata'
    COLUMNA = 'COLUMNA', 'Columna'
    TRABE = 'TRABE', 'Trabe/Viga'
    MURO = 'MURO', 'Muro'
    LOSA = 'LOSA', 'Losa'
    CIMENTACION = 'CIMENTACION', 'Cimentación'
    PAVIMENTO = 'PAVIMENTO', 'Pavimento'
    TERRACERIA = 'TERRACERIA', 'Terracería'
    DRENAJE = 'DRENAJE', 'Drenaje'
    OTRO = 'OTRO', 'Otro'

class EstadosElemento(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    REPLANTEO = 'REPLANTEO', 'En Replanteo'
    EXCAVACION = 'EXCAVACION', 'Excavación'
    CIMBRADO = 'CIMBRADO', 'Cimbrado'
    ARMADO = 'ARMADO', 'Armado de Acero'
    COLADO = 'COLADO', 'Colado'
    TERMINADO = 'TERMINADO', 'Terminado'




class ElementoConstructivo(AuditedModel):
    """
    Elementos específicos de la obra: zapatas, columnas, muros, etc.
    Cada elemento tiene coordenadas precisas
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='elementos')

    # Identificación
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200)


    tipo = models.CharField(max_length=20, choices=TiposElemento)

    # Coordenadas del elemento (centro o punto de control)
    latitud = models.FloatField()
    longitud = models.FloatField()
    elevacion = models.FloatField(help_text="Elevación en metros")

    # Coordenadas UTM (calculadas automáticamente)
    utm_este = models.FloatField(null=True, blank=True)
    utm_norte = models.FloatField(null=True, blank=True)
    utm_zona = models.IntegerField(null=True, blank=True)

    # Geometría (para elementos con área)
    area_proyecto = models.FloatField(
        null=True,
        blank=True,
        help_text="Área en m²"
    )
    volumen_proyecto = models.FloatField(
        null=True,
        blank=True,
        help_text="Volumen en m³"
    )
    longitud_proyecto = models.FloatField(
        null=True,
        blank=True,
        help_text="Longitud en m"
    )

    # Control de avance
    porcentaje_avance = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )


    estado = models.CharField(
        max_length=20,
        choices=EstadosElemento,
        default='PENDIENTE'
    )

    # Responsable
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='elementos_responsable'
    )

    # Fechas
    fecha_inicio_programada = models.DateField(null=True, blank=True)
    fecha_inicio_real = models.DateField(null=True, blank=True)
    fecha_fin_programada = models.DateField(null=True, blank=True)
    fecha_fin_real = models.DateField(null=True, blank=True)



    class Meta:
        verbose_name = "Elemento Constructivo"
        verbose_name_plural = "Elementos Constructivos"
        unique_together = ['proyecto', 'codigo']
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
