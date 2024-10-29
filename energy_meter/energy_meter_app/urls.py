from django.contrib import admin
from . import views
from django.urls import path

urlpatterns = [
    path('',views.index, name="index_page"),
    path('user_dashboard/',views.user_dashboard, name="user_dashboard"),
]
