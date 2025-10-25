"""
Management command to populate Ward data for Rupa Rural Municipality, Kaski
"""

from django.core.management.base import BaseCommand
from members.models import Ward


class Command(BaseCommand):
    help = 'Populate Ward data for Rupa Rural Municipality, Kaski'

    def handle(self, *args, **options):
        """Populate ward data"""
        
        # Ward data for Rupa Rural Municipality, Kaski
        wards_data = [
            {'ward_number': 1, 'ward_name': 'Ward 1', 'description': 'Central area of Rupa RM'},
            {'ward_number': 2, 'ward_name': 'Ward 2', 'description': 'Northern area of Rupa RM'},
            {'ward_number': 3, 'ward_name': 'Ward 3', 'description': 'Eastern area of Rupa RM'},
            {'ward_number': 4, 'ward_name': 'Ward 4', 'description': 'Southern area of Rupa RM'},
            {'ward_number': 5, 'ward_name': 'Ward 5', 'description': 'Western area of Rupa RM'},
            {'ward_number': 6, 'ward_name': 'Ward 6', 'description': 'North-eastern area of Rupa RM'},
            {'ward_number': 7, 'ward_name': 'Ward 7', 'description': 'South-eastern area of Rupa RM'},
            {'ward_number': 8, 'ward_name': 'Ward 8', 'description': 'North-western area of Rupa RM'},
            {'ward_number': 9, 'ward_name': 'Ward 9', 'description': 'South-western area of Rupa RM'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for ward_data in wards_data:
            ward, created = Ward.objects.get_or_create(
                ward_number=ward_data['ward_number'],
                defaults={
                    'ward_name': ward_data['ward_name'],
                    'description': ward_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created Ward {ward.ward_number}: {ward.ward_name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Ward {ward.ward_number} already exists')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nWard population completed!\n'
                f'Created: {created_count} wards\n'
                f'Already existed: {updated_count} wards'
            )
        )
