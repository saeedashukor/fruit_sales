import os.path

from django.views import generic
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db.models import ProtectedError
from django.template.loader import render_to_string
from itertools import chain
from datetime import datetime
from dateutil.relativedelta import *

from .models import City, Shop, WeeklySales, FruitSales, ShopOverheads
from .forms import CityForm, ShopForm, WeeklySalesForm


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
        date_str = str(self.kwargs['day']) + '-' + str(self.kwargs['month']) + '-' + str(self.kwargs['year'])
        date = datetime.strptime(date_str, '%d-%b-%Y')
        shop = Shop.objects.get(code=self.kwargs['shop_code'])
        context['weekly_sales'] = WeeklySales.objects.get(shop=shop, date=date)
        context['fruit_sales'] = FruitSales.objects.filter(weekly_sales=context['weekly_sales'])
        context['shop_overheads'] = ShopOverheads.objects.filter(weekly_sales=context['weekly_sales'])
        context['base_template'] = 'sales/weekly_sales_page.html'
        return context


def weekly_sales_form(request):
    shops = Shop.objects.all()
    context = {'shops': shops,
               'weekly_sales': '',
               'fruit_sales': '',
               'shop_overheads': ''}

    if request.method == 'POST':
        context['base_template'] = 'sales/weekly_sales_page.html'
        date = request.POST.get('date')
        shop_name = request.POST.get('shop')
        date_ = datetime.strptime(str(date), "%Y-%m-%d")
        shop = Shop.objects.get(name=shop_name)
        if date_.weekday() != 0:
            monday = date_ + relativedelta(weekday=MO(-1))
            context['weekly_sales'] = WeeklySales.objects.get(shop=shop, date=monday)
        else:
            context['weekly_sales'] = WeeklySales.objects.get(shop=shop, date=date)
        context['fruit_sales'] = FruitSales.objects.filter(weekly_sales=context['weekly_sales'])
        context['shop_overheads'] = ShopOverheads.objects.filter(weekly_sales=context['weekly_sales'])
    else:
        context['base_template'] = 'sales/weekly_sales_form.html'
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
