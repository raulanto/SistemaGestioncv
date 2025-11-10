from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from .audited_model import AuditedModel
from .project_model import Proyecto

class VolumenTerraceria(AuditedModel):
    """Cálculo de volúmenes de corte y relleno"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='volumenes')

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    # Área del cálculo (polígono definido por puntos)
    # En producción usarías GeoDjango con PolygonField
    area_m2 = models.FloatField()

    # Volúmenes calculados
    volumen_corte_m3 = models.FloatField(default=0)
    volumen_relleno_m3 = models.FloatField(default=0)
    volumen_neto_m3 = models.FloatField(default=0)  # corte - relleno

    # Método de cálculo
    METODOS = [
        ('SECCIONES', 'Áreas de Secciones'),
        ('GRID', 'Retícula (Grid)'),
        ('TIN', 'Triangulación (TIN)'),
        ('CURVAS', 'Curvas de Nivel'),
    ]
    metodo_calculo = models.CharField(max_length=20, choices=METODOS)

    # Fechas
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    calculado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Datos del levantamiento
    archivo_levantamiento = models.FileField(
        upload_to='levantamientos/',
        null=True,
        blank=True,
        help_text="Archivo CSV con coordenadas del levantamiento"
    )

    class Meta:
        verbose_name = "Volumen de Terracería"
        verbose_name_plural = "Volúmenes de Terracería"
        ordering = ['-fecha_calculo']

    def __str__(self):
        return f"{self.nombre} - {self.fecha_calculo.date()}"
