import uuid
from django.db import models
from django.core.validators import MinValueValidator
from .audited_model import AuditedModel

class ElementoConceptoRelacion(AuditedModel):
    """
    Tabla intermedia que conecta los elementos físicos de la obra con los conceptos del presupuesto.
    Un elemento puede consumir de varios conceptos y un concepto aplicarse a varios elementos.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    elemento = models.ForeignKey(
        'gestor.ElementoConstructivo', 
        on_delete=models.CASCADE, 
        related_name='conceptos_asignados'
    )
    concepto = models.ForeignKey(
        'gestor.ConceptoPresupuesto', 
        on_delete=models.CASCADE, 
        related_name='elementos_relacionados'
    )
    cantidad_asignada = models.DecimalField(
        max_digits=14, 
        decimal_places=4,
        validators=[MinValueValidator(0)],
        help_text="Cantidad del concepto asignada a este elemento"
    )

    class Meta:
        verbose_name = "Relación Elemento-Concepto"
        verbose_name_plural = "Relaciones Elementos-Conceptos"
        unique_together = ['elemento', 'concepto']

    def __str__(self):
        return f"{self.elemento.codigo} -> {self.concepto.clave} ({self.cantidad_asignada})"


class NumeroGenerador(AuditedModel):
    """
    Medición real en campo de cuánto se ejecutó de cada concepto.
    Se cuelga de un Reporte de Avance para no duplicar el flujo de captura en campo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte_avance = models.ForeignKey(
        'gestor.ReporteAvance', 
        on_delete=models.CASCADE, 
        related_name='numeros_generadores'
    )
    concepto = models.ForeignKey(
        'gestor.ConceptoPresupuesto', 
        on_delete=models.CASCADE, 
        related_name='numeros_generadores'
    )
    cantidad_ejecutada = models.DecimalField(
        max_digits=14, 
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    fecha_medicion = models.DateField(
        help_text="Fecha real en que se realizó la medición física"
    )

    class Meta:
        verbose_name = "Número Generador"
        verbose_name_plural = "Números Generadores"
        ordering = ['-fecha_medicion', '-created_at']

    def __str__(self):
        return f"Gen: {self.concepto.clave} - {self.cantidad_ejecutada} {self.concepto.unidad}"
