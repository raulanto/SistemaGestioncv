import uuid
from django.db import models
from django.core.validators import MinValueValidator
from .audited_model import AuditedModel

class Material(AuditedModel):
    """
    Catálogo global de materiales disponibles.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200, unique=True, help_text="Nombre del material (ej. Cemento Cruz Azul)")
    unidad_medida = models.CharField(max_length=50, help_text="Ej. bulto, ton, m3, pza, litro")
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.unidad_medida})"


class InventarioProyecto(AuditedModel):
    """
    Inventario de materiales asignados a un proyecto específico.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(
        'gestor.Proyecto', 
        on_delete=models.CASCADE, 
        related_name='inventario_materiales'
    )
    material = models.ForeignKey(
        Material, 
        on_delete=models.CASCADE, 
        related_name='inventarios'
    )
    stock_total_ingresado = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cantidad total de material que ha entrado al proyecto"
    )
    stock_disponible = models.FloatField(
        default=0,
        help_text="Cantidad actual disponible en el proyecto"
    )
    costo_unitario_estimado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Costo unitario referencial para presupuestos"
    )

    class Meta:
        verbose_name = "Inventario de Proyecto"
        verbose_name_plural = "Inventarios de Proyectos"
        unique_together = ['proyecto', 'material']
        ordering = ['proyecto__codigo', 'material__nombre']

    def __str__(self):
        return f"{self.material.nombre} - {self.proyecto.codigo} (Disp: {self.stock_disponible})"


class MaterialUtilizado(AuditedModel):
    """
    Registro del consumo de un material dentro de un Reporte de Avance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporte = models.ForeignKey(
        'gestor.ReporteAvance', 
        on_delete=models.CASCADE, 
        related_name='materiales_utilizados_rel'
    )
    inventario = models.ForeignKey(
        InventarioProyecto, 
        on_delete=models.CASCADE, 
        related_name='consumos'
    )
    cantidad_utilizada = models.FloatField(
        validators=[MinValueValidator(0.01)],
        help_text="Cantidad consumida en la unidad de medida del material"
    )
    notas = models.TextField(blank=True, help_text="Observaciones sobre el uso de este material")

    class Meta:
        verbose_name = "Material Utilizado"
        verbose_name_plural = "Materiales Utilizados"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.cantidad_utilizada} {self.inventario.material.unidad_medida} de {self.inventario.material.nombre}"

    def save(self, *args, **kwargs):
        # Descuento automático del stock disponible al crear un nuevo registro
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            self.inventario.stock_disponible -= self.cantidad_utilizada
            self.inventario.save(update_fields=['stock_disponible', 'updated_at'])
