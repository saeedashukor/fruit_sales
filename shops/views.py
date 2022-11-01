from django.views import generic
from django.shortcuts import render, get_object_or_404
from itertools import chain

from .models import City, Shop


class IndexView(generic.ListView):
    template_name = 'home.html'

    def get_queryset(self):
        city_model = City.objects.all()
        shop_model = Shop.objects.all()
        # returning multiple QuerySets
        return list(chain(city_model, shop_model))


def show_cities(request):
    cities = City.objects.all()
    return render(request, 'cities/city.html', {'cities': cities})


def city_details(request, city_id):
    city = get_object_or_404(City, pk=city_id)
    return render(request, 'cities/city_details.html', {'city': city})


def show_shops(request):
    shops = Shop.objects.all()
    return render(request, 'shops/shop.html', {'shops': shops})


def shop_details(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    return render(request, 'shops/shop_details.html', {'shop': shop})
