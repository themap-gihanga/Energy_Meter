from django.urls import path
from . import views

urlpatterns = [
    path('customer_service/',views.customer_service, name="customer_service"),
    path('buy_power/',views.buy_power_form, name="buy_power_form"),
    path('check-power/',views.check_power, name="check_power"),
    path('profile/',views.update_profile, name="update_profile"),
]
