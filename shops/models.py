from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)


class Shop(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField(max_length=300)
    postcode = models.CharField(max_length=10)
    year_opened = models.DateTimeField()
