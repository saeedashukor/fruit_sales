from django.urls import path
from .models import WeeklySales
from . import views

app_name = 'shops'
urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('city/', views.CitiesView.as_view(), name='city'),
    path('city/<int:pk>', views.CityDetails.as_view(), name='city_details'),
    path('city/add_city', views.city_forms, name='city_forms'),
    path('shop/', views.ShopsView.as_view(), name='shop'),
    path('shop/<int:pk>', views.ShopDetails.as_view(), name='shop_details'),
    path('shop/add_shop', views.shop_forms, name='shop_forms'),
    path('city/<int:pk>/delete', views.DeleteCity.as_view(), name='delete_city'),
    path('shop/<int:pk>/delete', views.DeleteShop.as_view(), name='delete_shop'),
    path('weekly_import/<int:pk>/<int:year>/<str:month>/<int:day>/<str:shop_code>', views.WeeklySalesView.as_view(
        date_field='date', model=WeeklySales), name='weekly_sales'),
    path('weekly_import/', views.view_weekly_sales_form, name='view_weekly_sales_form'),
    path('upload/', views.upload_file, name='upload_weekly_data'),
    path('fruit_income/all', views.view_fruit_income_all, name='view_fruit_income_all')
]
