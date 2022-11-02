from django import forms
import datetime
from .models import City


class CityForm(forms.Form):
    name = forms.CharField(label='City name', max_length=100)


class ShopForm(forms.Form):
    class CityNameChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return f'{obj.name}'

    city = CityNameChoiceField(queryset=City.objects.all())
    name = forms.CharField(label='Shop name', max_length=200)
    code = forms.CharField(label='Shop code, eg: ShopA, Shop9', max_length=10)
    address = forms.CharField(label='Address', max_length=300)
    postcode = forms.CharField(label='Postcode', max_length=5)
    year_opened = forms.IntegerField(label='Year opened', min_value=1900, max_value=datetime.datetime.now().year)


