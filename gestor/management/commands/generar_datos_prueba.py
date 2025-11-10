# ============================================
# GENERADOR DE DATOS DE PRUEBA
# ============================================
# management/commands/generar_datos_prueba.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Importar tus modelos
from gestor.models import (
    Proyecto,
    ElementoConstructivo,
    PuntoControl,
    Cuadrilla,
    ReporteAvance,
    VolumenTerraceria
)


class Command(BaseCommand):
    help = 'Genera datos de prueba para el sistema de obras civiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--proyectos',
            type=int,
            default=3,
            help='Número de proyectos a crear'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina datos existentes antes de generar nuevos'
        )

    def handle(self, *args, **options):
        if options['limpiar']:
            self.stdout.write('🗑️  Limpiando datos existentes...')
            self.limpiar_datos()

        self.stdout.write('🚀 Generando datos de prueba...\n')

        # Crear usuarios
        usuarios = self.crear_usuarios()
        self.stdout.write(self.style.SUCCESS(f'✅ {len(usuarios)} usuarios creados'))

        # Crear proyectos
        num_proyectos = options['proyectos']
        proyectos = []
        for i in range(num_proyectos):
            proyecto = self.crear_proyecto(i + 1, usuarios)
            proyectos.append(proyecto)

            # Crear elementos para cada proyecto
            elementos = self.crear_elementos(proyecto, usuarios)
            self.stdout.write(f'  └─ {len(elementos)} elementos creados')

            # Crear puntos de control
            puntos = self.crear_puntos_control(proyecto, elementos, usuarios)
            self.stdout.write(f'  └─ {len(puntos)} puntos de control')

            # Crear cuadrillas
            cuadrillas = self.crear_cuadrillas(proyecto, elementos, usuarios)
            self.stdout.write(f'  └─ {len(cuadrillas)} cuadrillas')

            # Crear reportes de avance
            reportes = self.crear_reportes(elementos, cuadrillas, usuarios)
            self.stdout.write(f'  └─ {len(reportes)} reportes de avance')

            # Crear cálculos de volumen
            volumenes = self.crear_volumenes(proyecto, usuarios)
            self.stdout.write(f'  └─ {len(volumenes)} cálculos de volumen\n')

        self.stdout.write(self.style.SUCCESS(f'\n✨ Datos generados exitosamente!'))
        self.mostrar_resumen(proyectos)

    def limpiar_datos(self):
        """Elimina todos los datos de prueba"""
        ReporteAvance.objects.all().delete()
        VolumenTerraceria.objects.all().delete()
        PuntoControl.objects.all().delete()
        Cuadrilla.objects.all().delete()
        ElementoConstructivo.objects.all().delete()
        Proyecto.objects.all().delete()
        User.objects.filter(username__startswith='test_').delete()

    def crear_usuarios(self):
        """Crea usuarios de prueba"""
        usuarios = []

        roles = [
            ('director', 'Director', 'Obra'),
            ('residente', 'Residente', 'Obra'),
            ('topografo', 'Juan', 'Topógrafo'),
            ('supervisor', 'María', 'Supervisora'),
            ('jefe_cuadrilla_1', 'Pedro', 'Martínez'),
            ('jefe_cuadrilla_2', 'Luis', 'García'),
            ('jefe_cuadrilla_3', 'Carlos', 'López'),
        ]

        for username, first_name, last_name in roles:
            user, created = User.objects.get_or_create(
                username=f'test_{username}',
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@obratest.com',
                    'is_staff': True
                }
            )
            if created:
                user.set_password('test123')
                user.save()
            usuarios.append(user)

        return usuarios

    def crear_proyecto(self, numero, usuarios):
        """Crea un proyecto de prueba"""

        proyectos_plantilla = [
            {
                'nombre': 'Autopista Querétaro-San Luis Potosí Tramo 3',
                'codigo': 'AUT-QRO-SLP-T3',
                'cliente': 'SCT - Secretaría de Comunicaciones',
                'lat': 20.5888,
                'lon': -100.3899,
                'zona_utm': 14,
                'presupuesto': 125000000,
            },
            {
                'nombre': 'Centro Comercial Plaza del Sol',
                'codigo': 'CC-PLAZA-SOL',
                'cliente': 'Desarrollos Inmobiliarios del Bajío',
                'lat': 20.6597,
                'lon': -103.3496,
                'zona_utm': 13,
                'presupuesto': 45000000,
            },
            {
                'nombre': 'Planta Industrial Aeroespacial',
                'codigo': 'IND-AERO-01',
                'cliente': 'Safran Aircraft Engines México',
                'lat': 20.6230,
                'lon': -100.4052,
                'zona_utm': 14,
                'presupuesto': 78000000,
            },
        ]

        plantilla = proyectos_plantilla[(numero - 1) % len(proyectos_plantilla)]

        fecha_inicio = timezone.now().date() - timedelta(days=random.randint(30, 180))
        duracion_dias = random.randint(180, 540)

        proyecto = Proyecto.objects.create(
            nombre=plantilla['nombre'],
            codigo=plantilla['codigo'],
            descripcion=f'Proyecto de construcción {plantilla["nombre"]}. Incluye diseño, construcción y supervisión.',
            cliente=plantilla['cliente'],
            sistema_coordenadas='UTM',
            zona_utm=plantilla['zona_utm'],
            hemisferio='N',
            lat_referencia=plantilla['lat'],
            lon_referencia=plantilla['lon'],
            elevacion_referencia=random.uniform(1800, 2400),
            director_obra=usuarios[0],
            residente_obra=usuarios[1],
            fecha_inicio=fecha_inicio,
            fecha_fin_estimada=fecha_inicio + timedelta(days=duracion_dias),
            estado=random.choice(['PLAN', 'EJECUCION', 'EJECUCION', 'EJECUCION']),
            presupuesto_total=Decimal(plantilla['presupuesto'])
        )

        self.stdout.write(self.style.SUCCESS(f'✅ Proyecto: {proyecto.codigo}'))
        return proyecto

    def crear_elementos(self, proyecto, usuarios):
        """Crea elementos constructivos para un proyecto"""
        elementos = []

        # Determinar tipos de elementos según el proyecto
        if 'Autopista' in proyecto.nombre:
            tipos_config = [
                ('TERRACERIA', 'Terracería', 15),
                ('PAVIMENTO', 'Pavimento', 20),
                ('DRENAJE', 'Obra de Drenaje', 10),
                ('PUENTE', 'Estructura', 5),
            ]
        elif 'Centro Comercial' in proyecto.nombre or 'Plaza' in proyecto.nombre:
            tipos_config = [
                ('ZAPATA', 'Zapata', 25),
                ('COLUMNA', 'Columna', 30),
                ('TRABE', 'Trabe', 35),
                ('LOSA', 'Losa', 15),
                ('MURO', 'Muro', 20),
            ]
        else:  # Industrial
            tipos_config = [
                ('CIMENTACION', 'Cimentación', 20),
                ('COLUMNA', 'Columna', 25),
                ('TRABE', 'Trabe', 30),
                ('LOSA', 'Losa Industrial', 15),
            ]

        contador = 1

        # Crear elementos en un área alrededor del punto de referencia
        for tipo, nombre_base, cantidad in tipos_config:
            for i in range(cantidad):
                # Generar coordenadas aleatorias en un radio de ~1km
                offset_lat = random.uniform(-0.009, 0.009)
                offset_lon = random.uniform(-0.009, 0.009)

                lat = proyecto.lat_referencia + offset_lat
                lon = proyecto.lon_referencia + offset_lon
                elev = proyecto.elevacion_referencia + random.uniform(-5, 15)

                # Estado realista basado en el avance
                estados_posibles = ['PENDIENTE', 'REPLANTEO', 'EXCAVACION',
                                    'CIMBRADO', 'ARMADO', 'COLADO', 'TERMINADO']

                # Más elementos terminados al inicio, menos al final
                peso_estado = [0.1, 0.15, 0.2, 0.15, 0.15, 0.15, 0.1]
                estado = random.choices(estados_posibles, weights=peso_estado)[0]

                # Porcentaje según estado
                porcentaje_map = {
                    'PENDIENTE': random.uniform(0, 10),
                    'REPLANTEO': random.uniform(10, 25),
                    'EXCAVACION': random.uniform(25, 45),
                    'CIMBRADO': random.uniform(45, 60),
                    'ARMADO': random.uniform(60, 80),
                    'COLADO': random.uniform(80, 95),
                    'TERMINADO': 100,
                }
                porcentaje = porcentaje_map[estado]

                # Fechas programadas
                dias_offset = contador * 3
                fecha_inicio = proyecto.fecha_inicio + timedelta(days=dias_offset)
                duracion = random.randint(5, 30)
                fecha_fin = fecha_inicio + timedelta(days=duracion)

                # Si está terminado, tiene fecha real
                fecha_fin_real = None
                if estado == 'TERMINADO':
                    fecha_fin_real = fecha_fin - timedelta(days=random.randint(-5, 5))

                elemento = ElementoConstructivo.objects.create(
                    proyecto=proyecto,
                    codigo=f'{proyecto.codigo}-{tipo[:3]}-{str(i + 1).zfill(3)}',
                    nombre=f'{nombre_base} {i + 1}',
                    tipo=tipo,
                    latitud=lat,
                    longitud=lon,
                    elevacion=elev,
                    # UTM se calculará después con tu API
                    utm_este=None,
                    utm_norte=None,
                    utm_zona=proyecto.zona_utm,
                    area_proyecto=random.uniform(10, 200) if tipo in ['LOSA', 'PAVIMENTO'] else None,
                    volumen_proyecto=random.uniform(5, 100) if tipo in ['ZAPATA', 'CIMENTACION'] else None,
                    longitud_proyecto=random.uniform(5, 50) if tipo in ['TRABE', 'MURO'] else None,
                    porcentaje_avance=porcentaje,
                    estado=estado,
                    responsable=random.choice(usuarios[2:5]),
                    fecha_inicio_programada=fecha_inicio,
                    fecha_inicio_real=fecha_inicio if estado != 'PENDIENTE' else None,
                    fecha_fin_programada=fecha_fin,
                    fecha_fin_real=fecha_fin_real,
                )

                elementos.append(elemento)
                contador += 1

        return elementos

    def crear_puntos_control(self, proyecto, elementos, usuarios):
        """Crea puntos de control topográfico"""
        puntos = []

        # Crear algunos puntos para elementos aleatorios
        elementos_muestra = random.sample(
            list(elementos),
            min(20, len(elementos))
        )

        equipos = ['GPS_RTK', 'GPS_DIFERENCIAL', 'ESTACION_TOTAL', 'NIVEL']
        tipos = ['BENCHMARK', 'REPLANTEO', 'VERIFICACION', 'CONTROL']

        for i, elemento in enumerate(elementos_muestra):
            # Pequeña variación en las coordenadas
            lat = elemento.latitud + random.uniform(-0.0001, 0.0001)
            lon = elemento.longitud + random.uniform(-0.0001, 0.0001)
            elev = elemento.elevacion + random.uniform(-0.5, 0.5)

            punto = PuntoControl.objects.create(
                proyecto=proyecto,
                elemento=elemento,
                numero_punto=f'PC-{str(i + 1).zfill(4)}',
                descripcion=f'Punto de control para {elemento.nombre}',
                tipo=random.choice(tipos),
                latitud=lat,
                longitud=lon,
                elevacion=elev,
                precision_horizontal=random.uniform(0.5, 3.0),
                precision_vertical=random.uniform(0.5, 2.0),
                equipo_medicion=random.choice(equipos),
                topografo=usuarios[2],  # topógrafo
                validado=random.choice([True, True, True, False]),
                validado_por=usuarios[1] if random.random() > 0.3 else None,
                fecha_validacion=timezone.now() if random.random() > 0.3 else None,
                observaciones='Medición dentro de tolerancias' if random.random() > 0.5 else ''
            )
            puntos.append(punto)

        return puntos

    def crear_cuadrillas(self, proyecto, elementos, usuarios):
        """Crea cuadrillas de trabajo"""
        cuadrillas = []

        nombres_cuadrillas = [
            'Cuadrilla A - Cimentación',
            'Cuadrilla B - Estructura',
            'Cuadrilla C - Acabados',
            'Cuadrilla D - Terracería',
            'Cuadrilla E - Instalaciones',
        ]

        jefes = usuarios[4:7]  # Jefes de cuadrilla

        for i, nombre in enumerate(nombres_cuadrillas[:random.randint(3, 5)]):
            # Elementos que esta cuadrilla está trabajando
            elementos_cuadrilla = [e for e in elementos if e.estado in ['EXCAVACION', 'CIMBRADO', 'ARMADO']]
            elemento_actual = random.choice(elementos_cuadrilla) if elementos_cuadrilla else None

            # Ubicación actual (cerca del elemento actual)
            if elemento_actual:
                lat_actual = elemento_actual.latitud + random.uniform(-0.001, 0.001)
                lon_actual = elemento_actual.longitud + random.uniform(-0.001, 0.001)
            else:
                lat_actual = None
                lon_actual = None

            cuadrilla = Cuadrilla.objects.create(
                proyecto=proyecto,
                nombre=nombre,
                jefe_cuadrilla=jefes[i % len(jefes)],
                latitud_actual=lat_actual,
                longitud_actual=lon_actual,
                ultima_actualizacion=timezone.now() - timedelta(minutes=random.randint(5, 120)),
                elemento_actual=elemento_actual,
                activa=True
            )
            cuadrillas.append(cuadrilla)

        return cuadrillas

    def crear_reportes(self, elementos, cuadrillas, usuarios):
        """Crea reportes de avance"""
        reportes = []

        # Crear reportes para elementos con avance
        elementos_con_avance = [e for e in elementos if e.porcentaje_avance > 0]

        for elemento in elementos_con_avance:
            # Número de reportes según el avance
            num_reportes = int(elemento.porcentaje_avance / 25) + random.randint(0, 2)

            for i in range(num_reportes):
                # Fecha de reporte distribuida en el tiempo
                dias_atras = random.randint(1, 60)
                fecha_reporte = timezone.now().date() - timedelta(days=dias_atras)

                # Avance incremental
                avance_parcial = random.uniform(5, 25)

                reporte = ReporteAvance.objects.create(
                    elemento=elemento,
                    cuadrilla=random.choice(cuadrillas) if cuadrillas else None,
                    fecha=fecha_reporte,
                    hora=timezone.now().time(),
                    reportado_por=random.choice(usuarios[1:5]),
                    latitud=elemento.latitud + random.uniform(-0.0005, 0.0005),
                    longitud=elemento.longitud + random.uniform(-0.0005, 0.0005),
                    avance_cantidad=random.uniform(1, 50),
                    avance_porcentaje=min(100, avance_parcial * (i + 1)),
                    descripcion=self.generar_descripcion_reporte(elemento.tipo),
                    materiales_utilizados=self.generar_materiales(elemento.tipo),
                    personal_asignado=random.randint(3, 12),
                    horas_trabajadas=random.uniform(4, 10),
                    validado=random.choice([True, True, False]),
                    validado_por=usuarios[1] if random.random() > 0.3 else None
                )
                reportes.append(reporte)

        return reportes

    def crear_volumenes(self, proyecto, usuarios):
        """Crea cálculos de volúmenes"""
        volumenes = []

        for i in range(random.randint(2, 5)):
            # Generar volúmenes realistas
            corte = random.uniform(1000, 50000)
            relleno = random.uniform(1000, 50000)

            volumen = VolumenTerraceria.objects.create(
                proyecto=proyecto,
                nombre=f'Cálculo Terracería Zona {chr(65 + i)}',
                descripcion=f'Cálculo de movimiento de tierras para zona {chr(65 + i)}',
                area_m2=random.uniform(5000, 50000),
                volumen_corte_m3=corte,
                volumen_relleno_m3=relleno,
                volumen_neto_m3=corte - relleno,
                metodo_calculo=random.choice(['SECCIONES', 'GRID', 'TIN']),
                calculado_por=usuarios[1]
            )
            volumenes.append(volumen)

        return volumenes

    def generar_descripcion_reporte(self, tipo):
        """Genera descripciones realistas según el tipo de elemento"""
        descripciones = {
            'ZAPATA': [
                'Excavación completada según especificaciones',
                'Colocación de plantilla de concreto pobre',
                'Armado de acero de refuerzo verificado',
                'Colado de zapata realizado, concreto f\'c=250 kg/cm²'
            ],
            'COLUMNA': [
                'Inicio de armado de columna',
                'Cimbrado y aplomado de columna',
                'Revisión de separadores y recubrimientos',
                'Colado de columna nivel +3.50m'
            ],
            'PAVIMENTO': [
                'Compactación de subrasante al 95% Proctor',
                'Colocación de base hidráulica e=20cm',
                'Tendido y compactación de carpeta asfáltica',
                'Señalización horizontal completada'
            ],
            'TERRACERIA': [
                'Desmonte y despalme completado',
                'Corte en material tipo II',
                'Formación de terraplén, capa 1',
                'Conformación y compactación final'
            ],
        }

        if tipo in descripciones:
            return random.choice(descripciones[tipo])
        return f'Avance en {tipo} según programa'

    def generar_materiales(self, tipo):
        """Genera lista de materiales según el tipo"""
        materiales = {
            'ZAPATA': 'Concreto f\'c=250 kg/cm²: 45m³, Acero fy=4200: 2.1 ton',
            'COLUMNA': 'Concreto f\'c=300 kg/cm²: 12m³, Acero fy=4200: 850kg, Cimbra metálica: 35m²',
            'PAVIMENTO': 'Base hidráulica: 150m³, Carpeta asfáltica: 85 ton, Cemento asfáltico: 4.2 ton',
            'LOSA': 'Concreto f\'c=250 kg/cm²: 28m³, Malla electrosoldada 6x6-10/10: 320m²',
        }
        return materiales.get(tipo, 'Materiales según especificación')

    def mostrar_resumen(self, proyectos):
        """Muestra resumen de datos generados"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE DATOS GENERADOS'))
        self.stdout.write('=' * 60 + '\n')

        for proyecto in proyectos:
            self.stdout.write(f'🏗️  {proyecto.nombre}')
            self.stdout.write(f'    Código: {proyecto.codigo}')
            self.stdout.write(f'    Elementos: {proyecto.elementos.count()}')
            self.stdout.write(f'    Puntos Control: {proyecto.puntos_control.count()}')
            self.stdout.write(f'    Cuadrillas: {proyecto.cuadrillas.count()}')

            # Calcular avance general
            elementos = proyecto.elementos.all()
            avance = sum(e.porcentaje_avance for e in elementos) / len(elementos) if elementos else 0
            self.stdout.write(f'    Avance: {avance:.1f}%')
            self.stdout.write('')

        self.stdout.write('=' * 60)
        self.stdout.write('\n🔗 URLs útiles:')
        self.stdout.write('   Admin: http://localhost:8000/admin/')
        self.stdout.write('   API: http://localhost:8000/api/proyectos/')
        self.stdout.write('   Swagger: http://localhost:8000/api/docs/')
        self.stdout.write('\n👤 Usuarios de prueba:')
        self.stdout.write('   Username: test_director / test_residente / test_topografo')
        self.stdout.write('   Password: test123')
        self.stdout.write('')


# ============================================
# SCRIPT ALTERNATIVO: Ejecutar desde shell
# ============================================
"""
Para ejecutar directamente desde Django shell:

python manage.py shell

>>> from api.generar_datos import generar_datos_prueba
>>> generar_datos_prueba(num_proyectos=3, limpiar=True)
"""


def generar_datos_prueba(num_proyectos=3, limpiar=False):
    """Función auxiliar para generar desde shell"""
    from django.core.management import call_command

    args = ['--proyectos', str(num_proyectos)]
    if limpiar:
        args.append('--limpiar')

    call_command('generar_datos_prueba', *args)


