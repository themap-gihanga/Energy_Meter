from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name="index_page"),
    path('buy_power/',views.buy_power_form, name="buy_power_form"),
]
