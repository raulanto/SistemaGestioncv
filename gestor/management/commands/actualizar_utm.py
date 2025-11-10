from django.core.management.base import BaseCommand
import requests
from gestor.models import ElementoConstructivo


class Command(BaseCommand):
    help = 'Actualiza coordenadas UTM de todos los elementos'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Actualizando coordenadas UTM...')

        API_BASE = 'http://localhost:8000/api'
        elementos = ElementoConstructivo.objects.all()

        # Preparar datos para conversión por lotes
        coords = []
        elementos_list = []

        for elemento in elementos:
            coords.append({
                'latitude': elemento.latitud,
                'longitude': elemento.longitud
            })
            elementos_list.append(elemento)

        # Convertir en lotes de 100
        batch_size = 100
        total_actualizados = 0

        for i in range(0, len(coords), batch_size):
            batch_coords = coords[i:i + batch_size]
            batch_elementos = elementos_list[i:i + batch_size]

            try:
                response = requests.post(
                    f'{API_BASE}/coordinates/batch-convert/',
                    json={
                        'coordinates': batch_coords,
                        'to_system': 'utm'
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    resultados = response.json()['results']

                    for elemento, resultado in zip(batch_elementos, resultados):
                        if 'output' in resultado:
                            elemento.utm_este = resultado['output']['easting']
                            elemento.utm_norte = resultado['output']['northing']
                            elemento.utm_zona = resultado['output']['zone']
                            elemento.save(update_fields=['utm_este', 'utm_norte', 'utm_zona'])
                            total_actualizados += 1

                    self.stdout.write(f'  ✓ Lote {i // batch_size + 1}: {len(batch_coords)} elementos')
                else:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error en lote {i // batch_size + 1}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ {total_actualizados} elementos actualizados'))

