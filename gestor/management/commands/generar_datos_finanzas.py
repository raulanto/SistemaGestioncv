# ============================================
# GENERADOR DE DATOS DE PRESUPUESTO Y FINANZAS
# ============================================
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import timedelta
import random
from decimal import Decimal

from gestor.models import (
    Proyecto,
    ElementoConstructivo,
    ReporteAvance,
    ConceptoPresupuesto,
    ElementoConceptoRelacion,
    NumeroGenerador,
    Estimacion,
    EstimacionDetalle,
    Retencion,
    ConvenioModificatorio,
    GastoReal
)

class Command(BaseCommand):
    help = 'Genera datos de prueba para los módulos de Presupuesto, Estimaciones y Finanzas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina datos financieros existentes antes de generar nuevos'
        )

    def handle(self, *args, **options):
        if options['limpiar']:
            self.stdout.write('🗑️  Limpiando datos financieros existentes...')
            Retencion.objects.all().delete()
            GastoReal.objects.all().delete()
            ConvenioModificatorio.objects.all().delete()
            EstimacionDetalle.objects.all().delete()
            Estimacion.objects.all().delete()
            NumeroGenerador.objects.all().delete()
            ElementoConceptoRelacion.objects.all().delete()
            ConceptoPresupuesto.objects.all().delete()

        self.stdout.write('🚀 Generando datos financieros...\n')
        proyectos = Proyecto.objects.all()
        
        if not proyectos.exists():
            self.stdout.write(self.style.WARNING('⚠️  No hay proyectos. Ejecuta generar_datos_prueba primero.'))
            return

        for proyecto in proyectos:
            self.stdout.write(f'Generando datos para: {proyecto.codigo}')
            
            # 1. Conceptos de Presupuesto
            conceptos = self.crear_conceptos(proyecto)
            
            # 2. Relacionar con Elementos Constructivos
            elementos = ElementoConstructivo.objects.filter(proyecto=proyecto)
            relaciones = self.relacionar_elementos_conceptos(elementos, conceptos)
            
            # 3. Números Generadores (basados en Reportes de Avance)
            reportes = ReporteAvance.objects.filter(elemento__proyecto=proyecto)
            self.crear_numeros_generadores(reportes, relaciones)
            
            # 4. Estimaciones y Detalles
            self.crear_estimaciones(proyecto, conceptos)
            
            # 5. Finanzas (Gastos Reales, Convenios, Retenciones)
            self.crear_finanzas(proyecto)

        self.stdout.write(self.style.SUCCESS('\n✨ Datos financieros generados exitosamente!'))

    def crear_conceptos(self, proyecto):
        conceptos_data = [
            ('PRE-01', 'Trazo y nivelación topográfica', 'm2', 50, 150),
            ('EXC-01', 'Excavación por medios mecánicos', 'm3', 200, 500),
            ('CIM-01', 'Cimbrado en zapatas y contratrabes', 'm2', 350, 800),
            ('CON-01', 'Concreto f\'c=250 kg/cm2', 'm3', 2500, 120),
            ('ACE-01', 'Acero de refuerzo fy=4200 kg/cm2', 'kg', 35, 8000),
        ]
        
        conceptos = []
        for clave, desc, unidad, pu, cant in conceptos_data:
            concepto = ConceptoPresupuesto.objects.create(
                proyecto=proyecto,
                clave=clave,
                descripcion=desc,
                unidad=unidad,
                cantidad_contratada=Decimal(str(cant)),
                precio_unitario=Decimal(str(pu))
            )
            conceptos.append(concepto)
        
        self.stdout.write(f'  └─ {len(conceptos)} Conceptos creados')
        return conceptos

    def relacionar_elementos_conceptos(self, elementos, conceptos):
        relaciones = []
        for elemento in elementos:
            # Asignar 2 o 3 conceptos aleatorios a cada elemento
            conceptos_asignados = random.sample(conceptos, k=random.randint(2, min(3, len(conceptos))))
            for concepto in conceptos_asignados:
                # Asignar una cantidad aleatoria (ej: 10% al 40% del total del concepto)
                cant_asignada = concepto.cantidad_contratada * Decimal(str(random.uniform(0.1, 0.4)))
                rel = ElementoConceptoRelacion.objects.create(
                    elemento=elemento,
                    concepto=concepto,
                    cantidad_asignada=round(cant_asignada, 4)
                )
                relaciones.append(rel)
        
        self.stdout.write(f'  └─ {len(relaciones)} Relaciones Elemento-Concepto')
        return relaciones

    def crear_numeros_generadores(self, reportes, relaciones):
        generadores = []
        for reporte in reportes:
            # Encontrar los conceptos relacionados al elemento del reporte
            rels_elemento = [r for r in relaciones if r.elemento == reporte.elemento]
            if not rels_elemento:
                continue
                
            # Generar avance para 1 o 2 conceptos de ese elemento
            rels_avance = random.sample(rels_elemento, k=min(2, len(rels_elemento)))
            for rel in rels_avance:
                # El avance reportado es proporcional al porcentaje del reporte
                # Si el reporte dice avance 20%, generamos ~20% de la cantidad asignada
                factor = (reporte.avance_porcentaje / 100) * random.uniform(0.8, 1.2)
                cant_ejecutada = rel.cantidad_asignada * Decimal(str(factor))
                
                gen = NumeroGenerador.objects.create(
                    reporte_avance=reporte,
                    concepto=rel.concepto,
                    cantidad_ejecutada=round(cant_ejecutada, 4),
                    fecha_medicion=reporte.fecha if hasattr(reporte, 'fecha') else reporte.created_at.date()
                )
                generadores.append(gen)
                
        self.stdout.write(f'  └─ {len(generadores)} Números Generadores')

    def crear_estimaciones(self, proyecto, conceptos):
        fecha_inicio = proyecto.fecha_inicio
        fecha_fin = proyecto.fecha_fin_estimada or (fecha_inicio + timedelta(days=120))
        
        estimaciones = []
        meses = (fecha_fin.year - fecha_inicio.year) * 12 + fecha_fin.month - fecha_inicio.month
        meses = max(1, meses)
        
        # Crear 1 estimación por mes
        for i in range(meses):
            p_inicio = fecha_inicio + timedelta(days=30*i)
            p_fin = p_inicio + timedelta(days=29)
            
            # Obtener generadores de este periodo
            generadores = NumeroGenerador.objects.filter(
                concepto__proyecto=proyecto,
                fecha_medicion__gte=p_inicio,
                fecha_medicion__lte=p_fin
            )
            
            if not generadores.exists():
                continue
                
            est = Estimacion.objects.create(
                proyecto=proyecto,
                numero=i+1,
                periodo_inicio=p_inicio,
                periodo_fin=p_fin,
                estado='AUTORIZADA',
                autorizada_por=proyecto.director_obra
            )
            estimaciones.append(est)
            
            # Agrupar generadores por concepto
            detalles_acumulados = {}
            for gen in generadores:
                if gen.concepto_id not in detalles_acumulados:
                    detalles_acumulados[gen.concepto_id] = Decimal('0')
                detalles_acumulados[gen.concepto_id] += gen.cantidad_ejecutada
                
            for concepto_id, cant_periodo in detalles_acumulados.items():
                concepto = next(c for c in conceptos if c.id == concepto_id)
                
                # Calcular acumulado anterior
                acum_anterior = EstimacionDetalle.objects.filter(
                    estimacion__proyecto=proyecto,
                    concepto_id=concepto_id,
                    estimacion__numero__lt=est.numero
                ).aggregate(models.Sum('cantidad_periodo'))['cantidad_periodo__sum'] or Decimal('0')
                
                EstimacionDetalle.objects.create(
                    estimacion=est,
                    concepto=concepto,
                    cantidad_periodo=cant_periodo,
                    acumulado_anterior=acum_anterior
                )
                
            # Crear retención para la estimación (Ej. 5% de Fondo de Garantía)
            importe_est = EstimacionDetalle.objects.filter(estimacion=est).aggregate(
                t=models.Sum('importe_periodo'))['t'] or Decimal('0')
            
            if importe_est > 0:
                Retencion.objects.create(
                    estimacion=est,
                    tipo='FONDO_GARANTIA',
                    descripcion='5% Fondo de Garantía',
                    importe=round(importe_est * Decimal('0.05'), 2)
                )

        self.stdout.write(f'  └─ {len(estimaciones)} Estimaciones con Detalles y Retenciones')

    def crear_finanzas(self, proyecto):
        # 1 Convenio
        ConvenioModificatorio.objects.create(
            proyecto=proyecto,
            numero_convenio='CM-01',
            fecha_firma=proyecto.fecha_inicio + timedelta(days=45),
            ampliacion_monto=Decimal('150000.00'),
            ampliacion_dias=30,
            motivo='Obras adicionales por estabilización de taludes no previstos.'
        )
        self.stdout.write(f'  └─ 1 Convenio Modificatorio')
        
        # Gastos reales
        gastos_data = [
            ('MATERIAL', 'Factura de Cemento y Acero A-102', 120000.0),
            ('MANO_OBRA', 'Nómina Semana 1 a 4', 85000.0),
            ('MAQUINARIA', 'Renta Excavadora Mes 1', 45000.0),
            ('SUBCONTRATO', 'Estudio Topográfico Final', 15000.0),
        ]
        
        for tipo, desc, importe in gastos_data:
            GastoReal.objects.create(
                proyecto=proyecto,
                tipo=tipo,
                fecha_gasto=proyecto.fecha_inicio + timedelta(days=random.randint(10, 60)),
                descripcion=desc,
                importe=Decimal(str(importe)),
                factura=f'F-{random.randint(1000, 9999)}'
            )
        self.stdout.write(f'  └─ {len(gastos_data)} Gastos Reales')
