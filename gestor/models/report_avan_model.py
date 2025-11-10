from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from .element_model import ElementoConstructivo
from .cuadrilla_model import Cuadrilla
from .audited_model import AuditedModel

class ReporteAvance(AuditedModel):
    """Reportes diarios de avance con evidencia fotográfica"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    elemento = models.ForeignKey(
        ElementoConstructivo,
        on_delete=models.CASCADE,
        related_name='reportes'
    )
    cuadrilla = models.ForeignKey(
        Cuadrilla,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes'
    )

    # Información del reporte
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    reportado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Ubicación donde se tomó el reporte
    latitud = models.FloatField()
    longitud = models.FloatField()

    # Mediciones
    avance_cantidad = models.FloatField(
        help_text="Cantidad ejecutada en la unidad del concepto"
    )
    avance_porcentaje = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Evidencia
    foto = models.ImageField(upload_to='reportes_avance/', null=True, blank=True)
    descripcion = models.TextField()

    # Recursos utilizados
    materiales_utilizados = models.TextField(blank=True)
    personal_asignado = models.IntegerField(default=0)
    horas_trabajadas = models.FloatField(default=0)

    # Validación
    validado = models.BooleanField(default=False)
    validado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_validados'
    )

    class Meta:
        verbose_name = "Reporte de Avance"
        verbose_name_plural = "Reportes de Avance"
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"Reporte {self.elemento.codigo} - {self.fecha}"
