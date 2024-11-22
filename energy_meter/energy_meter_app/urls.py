from django.urls import path
from . import views

urlpatterns = [
    path('login_users/', views.login_users, name='login_users'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('add_user/', views.add_user_view, name='add_user'),
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('update-user/<int:user_id>/', views.update_user_view, name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('report_users/', views.report_users_view, name='report_users'),
    path('logout/', views.logout_view, name='logout'),
    path('add_meter/', views.add_meter, name='add_meter'),
    path('manage_meter/', views.manage_meter, name='manage_meter'),
    path('update_meter/<int:meter_id>/', views.update_meter, name='update_meter'),
    path('delete_meter/<int:meter_id>/', views.delete_meter, name='delete_meter'),
    path('report_meters/', views.report_meters_view, name='report_meters'),
    path('add_data/', views.add_data, name='add_data'),
    path('manage_data/', views.manage_data, name='manage_data'),
    path('update_data/<int:data_id>/', views.update_data, name='update_data'),
    path('delete_data/<int:data_id>/', views.delete_data, name='delete_data'),
    path('report_data/', views.report_data_view, name='report_data'),
]