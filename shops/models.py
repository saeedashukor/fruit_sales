from django.db import models
from django.core.validators import FileExtensionValidator


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class Shop(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField(max_length=300, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    year_opened = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}, {self.code}'


class WeeklySales(models.Model):
    date = models.DateField('pub_date')
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['xlsx'])],
                            null=True, blank=True)

    def __str__(self):
        return f'{self.shop} : {self.date}'


class Fruit(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.name}'


class FruitSales(models.Model):
    weekly_sales = models.ForeignKey(WeeklySales, on_delete=models.CASCADE)
    fruit = models.ForeignKey(Fruit, on_delete=models.PROTECT)
    units_bought = models.IntegerField()
    cost_per_unit = models.DecimalField(max_digits=6, decimal_places=2)
    units_sold = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=6, decimal_places=2)
    units_waste = models.IntegerField()

    def __str__(self):
        return f'{self.fruit}, {self.weekly_sales}: {self.units_sold}, {self.cost_per_unit}, {self.units_sold}, {self.price_per_unit}, {self.units_waste}'


class ShopOverheads(models.Model):
    class OverheadType(models.TextChoices):
        personnel = 'PERS', 'personnel'
        premises = 'PREM', 'premises'
        other_oh = 'OTHER', 'other overheads'

    weekly_sales = models.ForeignKey(WeeklySales, on_delete=models.CASCADE)
    overhead_type = models.CharField(max_length=10, choices=OverheadType.choices)
    cost = models.IntegerField()

    def __str__(self):
        return f'{self.weekly_sales}, {self.overhead_type}, {self.cost}'

