from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
import datetime as dt
from datetime import datetime
from .models import City, Shop, WeeklySales


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name']
        labels = {'name': ('City name')}


class ShopForm(ModelForm):
    year_opened = forms.IntegerField(label='Year opened', min_value=1900, max_value=dt.datetime.now().year)

    class Meta:
        model = Shop
        fields = ['city', 'name', 'code', 'address', 'postcode', 'year_opened']


class DateInput(forms.DateInput):
    input_type = 'date'


class ViewWeeklySalesForm(ModelForm):
    class Meta:
        model = WeeklySales
        fields = ['shop', 'date']
        labels = {'shop': ('Select shop'),
                  'date': ('Select date')}
        widgets = {'date': DateInput}


class UploadWeeklySalesForm(ModelForm):
    class Meta:
        model = WeeklySales
        fields = ['file']
        labels = {'file': ('Upload a file')}

    def parse_file(self, file):
        file_str = file.name
        file = file_str.strip('.xlsx')
        file = file.split('-')
        date, shop_code = '-'.join(file[:3]), file[3:][0]
        date = datetime.strptime(date, '%Y-%m-%d')
        return date, shop_code

    def clean(self):
        cleaned_data = super(UploadWeeklySalesForm, self).clean()
        file = cleaned_data.get('file')
        date, shop_code = self.parse_file(file)
        if not Shop.objects.filter(code=shop_code).exists():
            raise ValidationError(f'Shop with code {shop_code} does not exist')
        if date.weekday() != 0:
            raise ValidationError(f'Date ({date}) does not fall on a Monday')
        if date > datetime.today():
            raise ValidationError(f'Date of weekly sale record ({date}) exceeds today ({datetime.today()})')
        year_opened = Shop.objects.get(code=shop_code).year_opened
        if date.year < year_opened:
            raise ValidationError(
                f'Year of weekly sale record ({date.year}) is before year opened of Shop ({year_opened})')
        if WeeklySales.objects.filter(date=date, shop=Shop.objects.get(code=shop_code)).exists():
            raise ValidationError(f'A record already exists with the same date: {date} and shop code: {shop_code}')
        return cleaned_data