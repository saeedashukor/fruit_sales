from django.core.management.base import BaseCommand
from shops.models import City, Shop
from openpyxl import load_workbook


class Command(BaseCommand):

    def handle(self, *args, **options):
        response = input(
            "You're about to delete all existing shops & cities, do you wish to continue?\nPress 'n' to stop.\n")
        if response.lower() != 'n':
            Shop.objects.all().delete()
            City.objects.all().delete()

            # Read existing workbook (Excel file)
            wb = load_workbook(filename='shops.xlsx')
            ws = wb['Sheet']

            cities = {}

            for row_cells in ws.iter_rows(min_row=2):
                city_cell, shop_name_cell, shop_code_cell = row_cells
                city = city_cell.value
                shop_name = shop_name_cell.value
                shop_code = shop_code_cell.value

                if city not in cities:
                    new_city = City.objects.create(name=city)
                    cities[city] = new_city
                    new_city.save()

                random_date = '2010-01-01'
                new_shop = Shop.objects.create(city=City.objects.get(name=city),
                                               name=shop_name,
                                               code=shop_code,
                                               address='',
                                               postcode='',
                                               year_opened=random_date)
                new_shop.save()

            self.stdout.write(self.style.SUCCESS('Successfully imported shops & cities into database.'))
