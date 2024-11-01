from django.shortcuts import render, redirect

def index(request):
    return render(request, "energy_meter_client/index.html")

def buy_power_form(request):
    return render(request, "energy_meter_client/forms/buy_power_form.html")
