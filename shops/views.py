from django.views import generic
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.db.models import ProtectedError
from django.core.files.storage import default_storage
from django.contrib import messages

from itertools import chain
from datetime import datetime
from dateutil.relativedelta import *

from .models import City, Shop, WeeklySales
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

    def validate_file(file, date, shop_code):
        if not Shop.objects.filter(code=shop_code).exists():
            return False, f'Shop with code {shop_code} does not exist'

        if date.weekday() != 0:
            return False, f'Date ({date}) does not fall on a Monday'

        if date > datetime.today():
            return False, f'Date of weekly sale record ({date}) exceeds today ({datetime.today()})'

        year_opened = Shop.objects.get(code=shop_code).year_opened
        if date.year < year_opened:
            return False, f'Year of weekly sale record ({date.year}) is before year opened of Shop ({year_opened})'

        if WeeklySales.objects.filter(date=date, shop=Shop.objects.get(code=shop_code)).exists():
            return False, f'A record already exists with the same date: {date} and shop code: {shop_code}'

        return True, f'File {file.name} successfully uploaded'

    if request.method == 'POST':
        form = UploadWeeklySalesForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            date, shop_code = parse_file(file)
            success, message = validate_file(file, date, shop_code)

            if success:
                weekly_sales = form.instance
                weekly_sales.date = date
                weekly_sales.shop = Shop.objects.get(code=shop_code)
                form.save()
                default_storage.save('shops/uploads/' + request.FILES['file'].name, request.FILES['file'])
                messages.success(request, message)
                return HttpResponseRedirect(reverse('shops:upload_weekly_data'))
            else:
                messages.error(request, message)
    else:
        form = UploadWeeklySalesForm()
    return render(request, 'sales/upload_form.html', {'form': form})
