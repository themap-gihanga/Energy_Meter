from django.urls import path
from . import views
from energy_meter_client.views import *

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('add_meter/', views.add_meter, name='add_meter'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('customer_service/', customer_service, name="customer_service"),
    path('manage_meters/', views.manage_meters, name="manage_meters"),
    path('update_meter/<int:meter_id>/', views.update_meter, name="update_meter"),
    path('delete_meter/<int:meter_id>/', views.delete_meter, name="delete_meter"),
    path('report_meters/', views.report_meters, name="report_meters"),
    path('data_display/', views.data_display, name="data_display"),
    
]
