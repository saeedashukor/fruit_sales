from django.views import generic
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.db.models import ProtectedError, F, Sum
from django.core.files.storage import default_storage
from django.contrib import messages

from itertools import chain
from datetime import datetime
from dateutil.relativedelta import *

from .models import City, Shop, WeeklySales, Fruit, FruitSales
from .forms import CityForm, ShopForm, UploadWeeklySalesForm


class IndexView(generic.ListView):
    template_name = 'home.html'

    def get_queryset(self):
        city_model = City.objects.all()
        shop_model = Shop.objects.all()
        # returning multiple QuerySets
        return list(chain(city_model, shop_model))


class CitiesView(generic.ListView):
    model = City
    template_name = 'cities/city.html'

    def get_queryset(self):
        return City.objects.all()


class ShopsView(generic.ListView):
    model = Shop
    template_name = 'shops/shop.html'

    def get_queryset(self):
        return Shop.objects.all()


class CityDetails(generic.DetailView):
    model = City
    template_name = 'cities/city_details.html'

    def get_queryset(self):
        return City.objects.all()


class ShopDetails(generic.DetailView):
    model = Shop
    template_name = 'shops/shop_details.html'

    def get_queryset(self):
        return Shop.objects.all()


class DeleteCity(generic.DeleteView):
    model = City
    success_url = reverse_lazy('shops:city')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            raise Http404('Unable to delete city due to shop referencing it.')


class DeleteShop(generic.DeleteView):
    model = Shop
    success_url = reverse_lazy('shops:shop')


class WeeklySalesView(generic.DateDetailView):
    context_object_name = 'weekly_sales'
    model = WeeklySales
    template_name = 'sales/weekly_sales.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_str = f"{self.kwargs['day']}-{self.kwargs['month']}-{self.kwargs['year']}"
        date = datetime.strptime(date_str, '%d-%b-%Y')
        shop = Shop.objects.get(code=self.kwargs['shop_code'])
        weekly_sales = WeeklySales.objects.get(shop=shop, date=date)
        context['weekly_sales'] = weekly_sales
        context['fruit_sales'] = weekly_sales.fruitsales_set.all()
        context['shop_overheads'] = weekly_sales.shopoverheads_set.all()
        context['base_template'] = 'sales/weekly_sales_partial.html'
        return context


def view_weekly_sales_form(request):
    shops = Shop.objects.all()
    context = {'shops': shops}

    if request.method == 'POST':
        context['base_template'] = 'sales/weekly_sales_partial.html'
        date = request.POST.get('date')
        shop_data = request.POST.get('shop').split(',')
        shop_id = int(shop_data[0])
        shop_name = shop_data[1]
        date_ = datetime.strptime(str(date), "%Y-%m-%d")
        shop = Shop.objects.get(pk=shop_id, name=shop_name)
        if date_.weekday() != 0:
            weekly_sales = WeeklySales.objects.get(shop=shop,
                                                   date=date_ + relativedelta(weekday=MO(-1)))
        else:
            weekly_sales = WeeklySales.objects.get(shop=shop, date=date)
        context['weekly_sales'] = weekly_sales
        context['fruit_sales'] = weekly_sales.fruitsales_set.all()
        context['shop_overheads'] = weekly_sales.shopoverheads_set.all()
    else:
        context['base_template'] = 'sales/weekly_sales_base.html'
    return render(request, 'sales/weekly_sales.html', context)


def city_forms(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            City.objects.create(name=request.POST['name'])
            return HttpResponseRedirect(reverse('shops:city'))
    else:  # If GET method or any other method -> create blank form
        form = CityForm()

    return render(request, 'cities/add_city_form.html', {'form': form})


def shop_forms(request):
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            Shop.objects.create(city=City.objects.get(pk=request.POST['city']),
                                name=request.POST['name'],
                                code=request.POST['code'],
                                address=request.POST['address'],
                                postcode=request.POST['postcode'],
                                year_opened=request.POST['year_opened'])
            return HttpResponseRedirect(reverse('shops:shop'))
    else:  # If GET method or any other method -> create blank form
        form = ShopForm()

    return render(request, 'shops/add_shop_form.html', {'form': form})


def upload_file(request):
    def parse_file(file):
        file_str = file.name
        file = file_str.strip('.xlsx')
        file = file.split('-')
        date, shop_code = '-'.join(file[:3]), file[3:][0]
        date = datetime.strptime(date, '%Y-%m-%d')
        return date, shop_code

    if request.method == 'POST':
        form = UploadWeeklySalesForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            date, shop_code = parse_file(file)
            weekly_sales = form.instance
            weekly_sales.date = date
            weekly_sales.shop = Shop.objects.get(code=shop_code)
            form.save()
            default_storage.save('shops/uploads/' + request.FILES['file'].name, request.FILES['file'])
            return HttpResponseRedirect(reverse('shops:upload_weekly_data'))
        else:
            messages.error(request, 'Error')
    else:
        form = UploadWeeklySalesForm()
    return render(request, 'sales/upload_form.html', {'form': form})


def view_fruit_income_all(request):
    fruits, total_income = get_total_fruit_income()
    context = {'fruits': fruits, 'total_income': total_income}
    return render(request, 'fruit_income/fruit_income_all_shops.html', context)


def get_income_dates(start_date=None, end_date=None):
    if not start_date and not end_date:
        return WeeklySales.objects.values('date').distinct()
    else:
        return WeeklySales.objects.filter(date__lte=end_date, date__gte=start_date).values('date').distinct()


def get_fruit_income(fruit, start_date, end_date, shop=None):
    if not shop:
        return FruitSales.objects.filter(fruit__name=fruit,
                                         weekly_sales__date__range=(start_date, end_date)
                                         ).aggregate(income=Sum(F('units_sold') * F('price_per_unit')))
    else:
        return FruitSales.objects.filter(fruit__name=fruit,
                                         weekly_sales__shop=shop,
                                         weekly_sales__date__range=(start_date, end_date)
                                         ).aggregate(income=Sum(F('units_sold') * F('price_per_unit')))


def get_total_fruit_income(shop=None, start_date=None, end_date=None):
    fruits = list(Fruit.objects.values_list('name', flat=True))
    total_income = []
    dates = get_income_dates(start_date, end_date)
    for i in range(0, len(dates) - 4, 4):
        start_date = dates[i]['date'].strftime('%Y-%m-%d')
        end_date = dates[i + 3]['date'].strftime('%Y-%m-%d')
        fruit_income = {'date': start_date}
        for fruit in fruits:
            income = get_fruit_income(fruit, start_date, end_date, shop)
            if fruit == 'blauwe bes':
                fruit = 'blauwebes'
            fruit_income[fruit] = round(float(income['income']), 2)
        total_income.append(fruit_income)
    return fruits, total_income