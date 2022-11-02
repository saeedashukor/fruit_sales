from django.urls import path
from . import views

app_name = 'shops'
urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('city/', views.show_cities, name='city'),
    path('city/<int:city_id>', views.city_details, name='city_details'),
    path('city/add_city', views.city_forms, name='city_forms'),
    path('shop/', views.show_shops, name='shop'),
    path('shop/<int:shop_id>', views.shop_details, name='shop_details'),
    path('shop/add_shop', views.shop_forms, name='shop_forms')
]