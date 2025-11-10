import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from simple_history.models import HistoricalRecords

from .audited_model import AuditedModel


class SistemasCoiordenadas(models.TextChoices):
    WGS84 = 'WGS84', 'WGS84 (GPS)'
    UTM = 'UTM', 'Universal Transverse Mercator'
    LOCAL = 'LOCAL', 'Sistema Local'


class EstadosProyecto(models.TextChoices):
    PLANIFICACION = 'PLAN', 'Planificación'
    EJECUCION = 'EJECUCION', 'En Ejecución'
    PAUSADO = 'PAUSADO', 'Pausado'
    FINALIZADO = 'FINALIZADO', 'Finalizado'


class Proyecto(AuditedModel):
    """Proyecto de construcción principal"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    cliente = models.CharField(max_length=200)

    sistema_coordenadas = models.CharField(
        max_length=10,
        choices=SistemasCoiordenadas,
        default='UTM'
    )
    zona_utm = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(60)]
    )
    hemisferio = models.CharField(
        max_length=1,
        choices=[('N', 'Norte'), ('S', 'Sur')],
        null=True,
        blank=True
    )

    # Punto de referencia del proyecto (BenchMark)
    lat_referencia = models.FloatField(help_text="Latitud del punto de referencia")
    lon_referencia = models.FloatField(help_text="Longitud del punto de referencia")
    elevacion_referencia = models.FloatField(
        default=0,
        help_text="Elevación sobre nivel del mar (m)"
    )

    # Administración
    director_obra = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='proyectos_dirigidos'
    )
    residente_obra = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='proyectos_residencia'
    )

    # Fechas
    fecha_inicio = models.DateField()
    fecha_fin_estimada = models.DateField()
    fecha_fin_real = models.DateField(null=True, blank=True)

    estado = models.CharField(max_length=20, choices=EstadosProyecto, default='PLAN')

    # Presupuesto
    presupuesto_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    history = HistoricalRecords(use_base_model_db=False)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
