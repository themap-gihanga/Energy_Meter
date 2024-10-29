from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from . models import *


def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('user_dashboard')
            try:
                user_profile = UserProfile.objects.get(name=user.username)
                if user_profile.status == 'staff':
                    return redirect('user_dashboard')
                elif user_profile.status == 'client':
                    return redirect('user_dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, "Profile not found.")
                return redirect('index_page')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('index_page')
        
    return render(request, 'energy_meter_app/forms/index.html')


def user_dashboard(request):
    return render(request, 'energy_meter_app/dashboards/user_dashboard.html')
