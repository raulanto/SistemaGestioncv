from django.db import models
from django.contrib.auth.models import User

import uuid

from gestor.models.project_model import Proyecto
from gestor.models.element_model import ElementoConstructivo
from .audited_model import AuditedModel

class Cuadrilla(AuditedModel):
    """
    Equipos de trabajo en campo
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='cuadrillas')

    nombre = models.CharField(max_length=100)
    jefe_cuadrilla = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Ubicación actual en tiempo real
    latitud_actual = models.FloatField(null=True, blank=True)
    longitud_actual = models.FloatField(null=True, blank=True)
    ultima_actualizacion = models.DateTimeField(null=True, blank=True)

    # Actividad actual
    elemento_actual = models.ForeignKey(
        ElementoConstructivo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuadrillas_trabajando'
    )

    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cuadrilla"
        verbose_name_plural = "Cuadrillas"

    def __str__(self):
        return f"{self.nombre} - {self.proyecto.codigo}"
