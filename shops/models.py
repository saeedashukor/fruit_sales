from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class Shop(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    address = models.TextField(max_length=300, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    year_opened = models.IntegerField(max_length=4, null=True, blank=True)

    def __str__(self):
        return f'{self.name}, {self.code}, {self.city}, {self.address}, {self.postcode}, {self.year_opened}'
