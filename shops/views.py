from django.views import generic
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from itertools import chain
from django.http import HttpResponseRedirect, Http404
from django.db.models import ProtectedError

from .models import City, Shop
from .forms import CityForm, ShopForm


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

    # Override post()
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            raise Http404('Unable to delete city due to shop referencing it.')


class DeleteShop(generic.DeleteView):
    model = Shop
    success_url = reverse_lazy('shops:shop')


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
