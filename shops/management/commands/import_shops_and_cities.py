from django.core.management.base import BaseCommand
from openpyxl import load_workbook
import random
from datetime import datetime

from shops.models import City, Shop


class Command(BaseCommand):
    def delete_objects(self):
        Shop.objects.all().delete()
        City.objects.all().delete()

    def import_file(self, filename):
        # Read existing workbook (Excel file)
        wb = load_workbook(filename=filename)
        ws = wb['Sheet']
        cities = {}
        self.create_shops_cities(ws, cities)

    def create_shops_cities(self, ws, cities):
        for row_cells in ws.iter_rows(min_row=2):
            city, shop_name, shop_code = [cell.value for cell in row_cells]

            if city not in cities:
                cities[city] = City.objects.create(name=city)

            random_year = random.randrange(start=1980, stop=datetime.now().year)
            Shop.objects.create(city=City.objects.get(name=city),
                                name=shop_name,
                                code=shop_code,
                                address='',
                                postcode='',
                                year_opened=random_year)

    def handle(self, *args, **options):
        response = input(
            "You're about to delete all existing shops & cities, do you wish to continue?\nPress 'y' to continue.\n")
        if response != 'y':
            return

        self.delete_objects()
        self.import_file(filename='shops.xlsx')
        self.stdout.write(self.style.SUCCESS('Successfully imported shops & cities into database.'))
