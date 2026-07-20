from django.db import models
from .cuadrilla_model import Cuadrilla
from .point_control_model import PuntoControl


class Participante(models.Model):
    nombre = models.CharField(max_length=150)
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.SET_NULL, null=True, related_name='participantes')
    especialidad = models.CharField(max_length=100, help_text="Ej: Topógrafo, Operador, Peón")

    def __str__(self):
        return self.nombre


class ActividadParticipante(models.Model):
    ESTATUS_CHOICES = (
        (1, 'Programada'),
        (2, 'En Tránsito'),
        (3, 'Pausada por Clima/Material'),
        (4, 'En Ejecución'),
        (5, 'Finalizada'),
    )

    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name='actividades')
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.CASCADE, related_name='actividades_diarias')

    descripcion_tarea = models.TextField(help_text="Descripción exacta de la labor asignada")
    punto_control = models.ForeignKey(PuntoControl, on_delete=models.SET_NULL, null=True,
                                      help_text="Frente de trabajo o cadenamiento")

    # Reemplazamos PointField por campos decimales estándar para evitar el error de GDAL
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitud GPS")
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitud GPS")

    status = models.IntegerField(choices=ESTATUS_CHOICES, default=1)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.participante.nombre} - {self.get_status_display()}"