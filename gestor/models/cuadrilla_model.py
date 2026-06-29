from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid

from gestor.models.project_model import Proyecto
from gestor.models.element_model import ElementoConstructivo
from .audited_model import AuditedModel

class Cuadrilla(AuditedModel):
    """
    Equipos de trabajo en campo
    """

    # 1. ESTÁNDAR FORMULA: Usar TextChoices para tipos y estados
    class EstadoCuadrilla(models.TextChoices):
        ACTIVA = 'ACTIVA', _('Activa (En Campo)')
        INACTIVA = 'INACTIVA', _('Inactiva (Desarticulada)')
        DESCANSO = 'DESCANSO', _('En Descanso / Pausa')

    class Especialidad(models.TextChoices):
        TOPOGRAFIA = 'TOPOGRAFIA', _('Topografía')
        TERRACERIA = 'TERRACERIA', _('Terracería y Maquinaria')
        ALBANILERIA = 'ALBANILERIA', _('Albañilería')
        FIERREROS = 'FIERREROS', _('Acero / Fierreros')
        CARPINTEROS = 'CARPINTEROS', _('Carpintería / Cimbra')
        GENERAL = 'GENERAL', _('Ayudantes Generales')


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 2. CAMPOS DE IDENTIFICACIÓN
    nombre = models.CharField(
        max_length=100,
        help_text=_("Ej: Cuadrilla Alfa - Fierreros")
    )
    especialidad = models.CharField(
        max_length=20,
        choices=Especialidad.choices,
        default=Especialidad.GENERAL
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoCuadrilla.choices,
        default=EstadoCuadrilla.ACTIVA
    )

    # 3. RELACIÓN DE CONTEXTO ESTRUCTURAL
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='cuadrillas',
        verbose_name=_("Proyecto Asignado")
    )

    # ¿Qué están haciendo exactamente AHORA? (El corazón de tu requerimiento)
    elemento_actual = models.ForeignKey(
        ElementoConstructivo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuadrillas_asignadas',
        verbose_name=_("Actividad Actual (Frente de Trabajo)"),
        help_text=_("Elemento constructivo en el que están trabajando en este momento.")
    )

    # 4. RELACIONES DE RECURSOS HUMANOS (El listado de trabajadores)
    # El Cabo, Maestro de Obra o Topógrafo Jefe (1 persona)
    lider = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuadrillas_lideradas',
        verbose_name=_("Líder / Cabo")
    )

    # Los trabajadores operativos (N personas) - Relación Muchos a Muchos
    miembros = models.ManyToManyField(
        User,
        related_name='cuadrillas',
        blank=True,
        verbose_name=_("Integrantes Operativos")
    )

    # 5. AUDITORÍA (Campos estándar si no heredas de AuditedModel)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Cuadrilla")
        verbose_name_plural = _("Cuadrillas")
        # Por defecto, mostrar las activas primero y luego ordenar alfabéticamente
        ordering = ['-estado', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_especialidad_display()})"
