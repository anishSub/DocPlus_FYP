from django.core.management.base import BaseCommand
from find_hospital.models import Hospital
import requests
import time

class Command(BaseCommand):
    help = 'Geocode hospitals to get latitude and longitude using Nominatim API'

    def handle(self, *args, **options):
        hospitals = Hospital.objects.all()
        success_count = 0
        fail_count = 0

        self.stdout.write(self.style.WARNING(f'Starting geocoding for {hospitals.count()} hospitals...'))
        self.stdout.write(self.style.WARNING('Note: This uses Nominatim API - please respect rate limits'))
        self.stdout.write('')

        for hospital in hospitals:
            if hospital.latitude and hospital.longitude:
                self.stdout.write(f'Skipping {hospital.name} - already has coordinates')
                continue

            search_query = f"{hospital.name} {hospital.city} Nepal"
            
            try:
                response = requests.get(
                    'https://nominatim.openstreetmap.org/search',
                    params={
                        'format': 'json',
                        'limit': 1,
                        'q': search_query
                    },
                    headers={'User-Agent': 'DocPlus/1.0'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        hospital.latitude = float(data[0]['lat'])
                        hospital.longitude = float(data[0]['lon'])
                        hospital.save()
                        
                        success_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ {hospital.name} -> ({hospital.latitude}, {hospital.longitude})'
                            )
                        )
                    else:
                        fail_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'✗ {hospital.name} - Location not found')
                        )
                else:
                    fail_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ {hospital.name} - API error: {response.status_code}')
                    )
                
                # Respect Nominatim rate limits
                time.sleep(1)
                
            except Exception as e:
                fail_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ {hospital.name} - Error: {str(e)}')
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Geocoding complete!'))
        self.stdout.write(self.style.SUCCESS(f'Success: {success_count} hospitals'))
        self.stdout.write(self.style.SUCCESS(f'Failed: {fail_count} hospitals'))
        self.stdout.write('')
        self.stdout.write('You can now add a map to hospital_detail.html template using these coordinates')
