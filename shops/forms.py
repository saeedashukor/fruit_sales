from django.forms import ModelForm
from django import forms
import datetime
from .models import City, Shop


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name']
        labels = {'name': ('City name')}


class ShopForm(ModelForm):
    year_opened = forms.IntegerField(label='Year opened', min_value=1900, max_value=datetime.datetime.now().year)

    class Meta:
        model = Shop
        fields = ['city', 'name', 'code', 'address', 'postcode', 'year_opened']
