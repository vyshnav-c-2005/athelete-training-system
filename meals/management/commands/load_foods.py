import csv
import os
from django.core.management.base import BaseCommand
from meals.models import FoodItem

class Command(BaseCommand):
    help = 'Load foods from foods.csv'

    def handle(self, *args, **options):
        csv_path = 'foods.csv'
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'File {csv_path} not found'))
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                obj, created = FoodItem.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'category': row['category'],
                        'calories_per_100g': float(row['calories_per_100g']),
                        'protein_per_100g': float(row['protein_per_100g']),
                        'carbs_per_100g': float(row['carbs_per_100g']),
                        'fats_per_100g': float(row['fats_per_100g']),
                        'region': row['region'],
                    }
                )
                if created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully inserted {count} new foods.'))
        
        total = FoodItem.objects.count()
        kerala_count = FoodItem.objects.filter(region='kerala').count()
        global_count = FoodItem.objects.filter(region='global').count()
        
        self.stdout.write(f'Total foods: {total}')
        self.stdout.write(f'Kerala foods: {kerala_count}')
        self.stdout.write(f'Global foods: {global_count}')
