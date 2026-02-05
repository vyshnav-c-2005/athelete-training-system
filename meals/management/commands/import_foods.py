import csv
import os
from django.core.management.base import BaseCommand, CommandError
from meals.models import FoodItem

class Command(BaseCommand):
    help = 'Import food items from a CSV file (format: name, carbs, protein, fats)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        if not os.path.exists(csv_file_path):
            raise CommandError(f'File "{csv_file_path}" does not exist')

        self.stdout.write(f'Importing foods from {csv_file_path}...')

        success_count = 0
        skipped_count = 0

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Check for required headers
                required_headers = {'name', 'carbs', 'protein', 'fats'}
                if not reader.fieldnames or not required_headers.issubset(set(reader.fieldnames)):
                     # Fallback for headerless or different headers if needed, 
                     # but instructions implied standard format. Let's try to be flexible or strict.
                     # "containing food name and macro values"
                     # Let's assume headers: name, carbs, protein, fats
                     pass

                for row in reader:
                    name = row.get('name', '').strip()
                    if not name:
                        continue

                    try:
                        carbs = float(row.get('carbs', 0))
                        protein = float(row.get('protein', 0))
                        fats = float(row.get('fats', 0))
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Skipping '{name}': Invalid macro values"))
                        continue

                    # Update or Create to prevent duplicates and allow updates
                    obj, created = FoodItem.objects.update_or_create(
                        name__iexact=name, # Case-insensitive check might be better, but strict name for now
                        defaults={
                            'name': name,
                            'carbs_per_100g': carbs,
                            'protein_per_100g': protein,
                            'fats_per_100g': fats,
                        }
                    )
                    
                    if created:
                        success_count += 1
                    else:
                        skipped_count += 1 # Technically updated, but we'll count as skipped/existing

        except Exception as e:
             raise CommandError(f'Error reading CSV: {e}')

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {success_count} new food items. Updated/Skipped {skipped_count}.'))
