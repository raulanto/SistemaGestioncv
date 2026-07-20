import uuid
from django.db import models
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords
from .audited_model import AuditedModel

class ConceptoPresupuesto(AuditedModel):
    """
    Catálogo de conceptos de obra. Es el documento legal base del contrato.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(
        'gestor.Proyecto', 
        on_delete=models.CASCADE, 
        related_name='conceptos_presupuesto'
    )
    clave = models.CharField(max_length=50, help_text="Ej. CIM-001")
    descripcion = models.TextField()
    unidad = models.CharField(max_length=20, help_text="Ej. m2, m3, pza, kg")
    
    # Cantidad contratada puede tener decimales
    cantidad_contratada = models.DecimalField(
        max_digits=14, 
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    
    # Precio unitario y dinero siempre en DecimalField (con precisión adicional)
    precio_unitario = models.DecimalField(
        max_digits=14, 
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    
    # Importe calculado, nunca editable directamente
    importe_contratado = models.DecimalField(
        max_digits=16, 
        decimal_places=2,
        editable=False,
        default=0
    )

    history = HistoricalRecords(use_base_model_db=False)

    class Meta:
        verbose_name = "Concepto de Presupuesto"
        verbose_name_plural = "Conceptos de Presupuesto"
        unique_together = ['proyecto', 'clave']
        ordering = ['proyecto', 'clave']

    def __str__(self):
        return f"{self.clave} - {self.descripcion[:50]}"

    def save(self, *args, **kwargs):
        # Calcular importe al vuelo
        self.importe_contratado = round(self.cantidad_contratada * self.precio_unitario, 2)
        super().save(*args, **kwargs)
