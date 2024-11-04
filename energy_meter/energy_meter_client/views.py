from django.shortcuts import render, redirect
from energy_meter_app.models import *
from django.http import JsonResponse
from django.contrib import messages

def index(request):
    return render(request, "energy_meter_client/index.html")

def buy_power_form(request):
    if request.method == 'POST':
        if 'serial_number' in request.POST:
            serial_number = request.POST.get('serial_number')
            try:
                meter = Meter.objects.select_related('owner').get(serial_number=serial_number)
                request.session['serial_number'] = serial_number
                return JsonResponse({
                    'status': 'success',
                    'message': f'Meter verified! Owner: {meter.owner.name}'
                })
            except Meter.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid meter number or meter not registered.'
                })
        
        elif 'amount' in request.POST:
            serial_number = request.session.get('serial_number')
            if not serial_number:
                messages.error(request, 'Please verify meter number first.')
                return redirect('buy_power_form')
            
            amount = request.POST.get('amount')
            try:
                meter = Meter.objects.get(serial_number=serial_number)
                
                messages.success(request, 'Power purchase successful!')
                request.session.pop('serial_number', None)
                return redirect('buy_power_success')
            except Meter.DoesNotExist:
                messages.error(request, 'Invalid meter number.')
                return redirect('buy_power_form')
    
    return render(request, "energy_meter_client/forms/buy_power_form.html")

def check_power(request):
    if request.method == 'POST':
        if 'serial_number' in request.POST:
            serial_number = request.POST.get('serial_number')
            try:
                meter = Meter.objects.select_related('owner').get(serial_number=serial_number)
                latest_data = Data.objects.filter(serial_number=meter).latest('created_at')
                
                return JsonResponse({
                    'status': 'success',
                    'meter_info': {
                        'owner_name': meter.owner.name,
                        'remaining_energy': float(meter.remaining_energy),
                        'voltage': float(latest_data.voltage),
                        'current': float(latest_data.current),
                        'power': float(latest_data.power),
                        'energy_consumed': float(latest_data.energy),
                        'power_factor': float(latest_data.power_factor),
                        'unit_price': float(latest_data.unit_price),
                    }
                })
            except Meter.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid meter number or meter not registered.'
                })
            except Data.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No data available for this meter.'
                })
    
    return render(request, "energy_meter_client/check_power/check_power.html")
