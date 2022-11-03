from django.contrib import admin
from .models import City, Shop, Fruit, FruitSales, WeeklySales, ShopOverheads

# Register your models here.
admin.site.register(City)
admin.site.register(Shop)
admin.site.register(Fruit)
admin.site.register(FruitSales)
admin.site.register(WeeklySales)
admin.site.register(ShopOverheads)
