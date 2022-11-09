from django.core.management.base import BaseCommand
from openpyxl import load_workbook
from pathlib import Path
from datetime import datetime

from shops.models import Fruit, FruitSales, WeeklySales, ShopOverheads, Shop


class Command(BaseCommand):
    def delete_objects(self):
        for model in ShopOverheads, FruitSales, WeeklySales, Fruit:
            model.objects.all().delete()

    def import_files(self, directory):
        source_files = Path(directory).glob('*')
        pathname = directory + '/'
        files = [file.name for file in source_files]
        count = 0
        fruits = set()  # store all unique fruit names

        for file in files:
            self.load_file(pathname, file, fruits)
            count += 1
            print(f'Imported {count}/{len(files)}: {file}')

    def load_file(self, pathname, file, fruits):
        wb = load_workbook(filename=pathname + file)
        ws_fruit = wb['by fruit']
        ws_oh = wb['overheads']

        date, shop_code = self.parse_spreadsheet(file)
        shop = Shop.objects.get(code=shop_code)
        self.create_weekly_sales(date, shop, file)
        weekly_sales = WeeklySales.objects.get(date=date, shop=shop)

        for row_cells in ws_fruit.iter_rows(min_row=2):
            fruit, units_bought, cost, units_sold, price, wastage = [cell.value for cell in row_cells]

            if fruit not in fruits:
                fruits.add(fruit)
                self.create_fruit(fruit)
            self.create_fruit_sales(weekly_sales, fruit, units_bought, cost, units_sold, price, wastage)

        for row_cells in ws_oh.iter_rows(min_row=2):
            personnel, premises, others = [cell.value for cell in row_cells]
            self.create_overheads(weekly_sales, 'PERS', personnel)
            self.create_overheads(weekly_sales, 'PREM', premises)
            self.create_overheads(weekly_sales, 'OTHER', others)

    def create_fruit(self, fruit):
        Fruit.objects.create(name=fruit)

    def parse_spreadsheet(self, file):
        file_str = file.strip('.xlsx')
        temp = file_str.split('-')
        date, shop_code = '-'.join(temp[:3]), temp[3:][0]
        date = datetime.strptime(date, '%Y-%m-%d')
        return date, shop_code

    def create_weekly_sales(self, date, shop, file):
        WeeklySales.objects.create(date=date, shop=shop, file=file)

    def create_fruit_sales(self, weekly_sales, fruit, units_bought, cost, units_sold, price, wastage):
        fruit = Fruit.objects.get(name=fruit)
        FruitSales.objects.create(weekly_sales=weekly_sales,
                                  fruit=fruit,
                                  units_bought=units_bought,
                                  cost_per_unit=cost,
                                  units_sold=units_sold,
                                  price_per_unit=price,
                                  units_waste=wastage)

    def create_overheads(self, weekly_sales, overhead_type, cost):
        ShopOverheads.objects.create(weekly_sales=weekly_sales,
                                     overhead_type=overhead_type,
                                     cost=cost)

    def handle(self, *args, **options):
        response = input(
            "You're about to delete all existing weekly sales data for all shops, do you wish to continue?\nPress 'y' to continue.\n")
        if response != 'y':
            return

        self.delete_objects()
        print('Objects deleted. Importing files...')
        self.import_files(directory='weekly_shop_data')
        self.stdout.write(self.style.SUCCESS('Successfully imported weekly sales data for all shops into database.'))
