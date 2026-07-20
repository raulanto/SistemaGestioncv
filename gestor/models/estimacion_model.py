import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from .audited_model import AuditedModel

class EstadosEstimacion(models.TextChoices):
    BORRADOR = 'BORRADOR', 'Borrador'
    EN_REVISION = 'EN_REVISION', 'En Revisión'
    AUTORIZADA = 'AUTORIZADA', 'Autorizada'
    PAGADA = 'PAGADA', 'Pagada'

class Estimacion(AuditedModel):
    """
    Corte periódico que agrupa números generadores para cobrar.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(
        'gestor.Proyecto', 
        on_delete=models.CASCADE, 
        related_name='estimaciones'
    )
    numero = models.PositiveIntegerField(help_text="Consecutivo de la estimación (1, 2, 3...)")
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    estado = models.CharField(
        max_length=20, 
        choices=EstadosEstimacion, 
        default='BORRADOR'
    )
    autorizada_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='estimaciones_autorizadas',
        help_text="Usuario con rol para autorizar la estimación"
    )

    class Meta:
        verbose_name = "Estimación"
        verbose_name_plural = "Estimaciones"
        unique_together = ['proyecto', 'numero']
        ordering = ['proyecto', 'numero']

    def __str__(self):
        return f"Est. {self.numero} - {self.proyecto.codigo}"


class EstimacionDetalle(AuditedModel):
    """
    Detalle financiero de cuánto se está cobrando por cada concepto en esta estimación.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estimacion = models.ForeignKey(
        Estimacion, 
        on_delete=models.CASCADE, 
        related_name='detalles'
    )
    concepto = models.ForeignKey(
        'gestor.ConceptoPresupuesto', 
        on_delete=models.CASCADE, 
        related_name='detalles_estimaciones'
    )
    
    # Cantidad que se cobra en este periodo
    cantidad_periodo = models.DecimalField(
        max_digits=14, 
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    importe_periodo = models.DecimalField(
        max_digits=16, 
        decimal_places=2,
        editable=False,
        default=0
    )
    
    # Control de avance acumulado
    acumulado_anterior = models.DecimalField(
        max_digits=14, 
        decimal_places=4,
        default=0,
        help_text="Cantidad acumulada hasta la estimación anterior"
    )
    acumulado_actual = models.DecimalField(
        max_digits=14, 
        decimal_places=4,
        editable=False,
        default=0,
        help_text="Cantidad acumulada incluyendo este periodo"
    )

    class Meta:
        verbose_name = "Detalle de Estimación"
        verbose_name_plural = "Detalles de Estimación"
        unique_together = ['estimacion', 'concepto']
        ordering = ['estimacion', 'concepto__clave']

    def __str__(self):
        return f"Detalle Est. {self.estimacion.numero} - {self.concepto.clave}"

    def save(self, *args, **kwargs):
        # Calcular importes
        self.importe_periodo = round(self.cantidad_periodo * self.concepto.precio_unitario, 2)
        # El acumulado actual es el anterior + el del periodo
        self.acumulado_actual = self.acumulado_anterior + self.cantidad_periodo
        super().save(*args, **kwargs)
