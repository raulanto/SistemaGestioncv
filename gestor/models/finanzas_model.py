import uuid
from django.db import models
from django.core.validators import MinValueValidator
from .audited_model import AuditedModel

class TiposRetencion(models.TextChoices):
    FONDO_GARANTIA = 'FONDO_GARANTIA', 'Fondo de Garantía (5%)'
    AMORTIZACION_ANTICIPO = 'AMORTIZACION_ANTICIPO', 'Amortización de Anticipo'
    OTRO = 'OTRO', 'Otro'

class TiposGasto(models.TextChoices):
    MATERIAL = 'MATERIAL', 'Material'
    MANO_OBRA = 'MANO_OBRA', 'Mano de Obra'
    MAQUINARIA = 'MAQUINARIA', 'Maquinaria y Equipo'
    SUBCONTRATO = 'SUBCONTRATO', 'Subcontrato'
    INDIRECTO = 'INDIRECTO', 'Indirecto'

class Retencion(AuditedModel):
    """
    Controla retenciones o deductivas aplicadas a una estimación.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estimacion = models.ForeignKey(
        'gestor.Estimacion', 
        on_delete=models.CASCADE, 
        related_name='retenciones'
    )
    tipo = models.CharField(
        max_length=50, 
        choices=TiposRetencion, 
        default=TiposRetencion.FONDO_GARANTIA
    )
    descripcion = models.CharField(max_length=255, blank=True)
    importe = models.DecimalField(
        max_digits=16, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = "Retención"
        verbose_name_plural = "Retenciones"
        ordering = ['estimacion', 'tipo']

    def __str__(self):
        return f"{self.get_tipo_display()} - Est. {self.estimacion.numero} ({self.importe})"


class ConvenioModificatorio(AuditedModel):
    """
    Documento legal que ampara cambios en el monto o plazo del contrato original.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(
        'gestor.Proyecto', 
        on_delete=models.CASCADE, 
        related_name='convenios'
    )
    numero_convenio = models.CharField(max_length=50, help_text="Ej. CM-01")
    fecha_firma = models.DateField()
    
    ampliacion_monto = models.DecimalField(
        max_digits=16, 
        decimal_places=2,
        default=0,
        help_text="Importe adicional autorizado (puede ser negativo si es deductiva)"
    )
    ampliacion_dias = models.IntegerField(
        default=0,
        help_text="Días adicionales otorgados al plazo de ejecución"
    )
    motivo = models.TextField()

    class Meta:
        verbose_name = "Convenio Modificatorio"
        verbose_name_plural = "Convenios Modificatorios"
        ordering = ['proyecto', 'fecha_firma']

    def __str__(self):
        return f"Convenio {self.numero_convenio} - {self.proyecto.codigo}"


class GastoReal(AuditedModel):
    """
    Gastos reales efectuados por la constructora, para contrastar contra 
    lo ingresado en las estimaciones y calcular utilidad/pérdida.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(
        'gestor.Proyecto', 
        on_delete=models.CASCADE, 
        related_name='gastos_reales'
    )
    concepto = models.ForeignKey(
        'gestor.ConceptoPresupuesto', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='gastos_reales',
        help_text="Opcional. Para asociar el gasto directamente a un concepto específico."
    )
    tipo = models.CharField(
        max_length=50, 
        choices=TiposGasto,
        default=TiposGasto.MATERIAL
    )
    fecha_gasto = models.DateField()
    descripcion = models.CharField(max_length=255)
    importe = models.DecimalField(
        max_digits=16, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    factura = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Gasto Real"
        verbose_name_plural = "Gastos Reales"
        ordering = ['-fecha_gasto']

    def __str__(self):
        return f"{self.tipo} - {self.importe} ({self.fecha_gasto})"
