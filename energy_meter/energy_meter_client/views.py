from django.shortcuts import render, redirect
from energy_meter_app.models import *
from django.http import JsonResponse
from django.contrib import messages
from energy_meter_app.middleware import meter_auth_middleware
from energy_meter_app.views import *
from energy_meter_app.models import *
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

@meter_login_required
def customer_service(request):
    return render(request, "energy_meter_client/customer_service.html")

@csrf_exempt
@require_POST
@meter_login_required
def buy_power_form(request):
    if request.method == 'POST':
        # Step 1: Verify meter
        if 'serial_number' in request.POST and 'amount' not in request.POST:
            serial_number = request.POST.get('serial_number')
            try:
                meter = Meter.objects.get(serial_number=serial_number, is_active=True)
                return JsonResponse({
                    'status': 'success',
                    'message': 'Meter verified successfully',
                    'meter_info': {
                        'serial_number': meter.serial_number,
                        'name': meter.name,
                        'address': meter.address
                    }
                })
            except Meter.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid meter number or meter not active'
                }, status=400)
        
        # Step 2: Process purchase
        elif 'amount' in request.POST:
            serial_number = request.POST.get('serial_number')
            amount = float(request.POST.get('amount'))
            
            try:
                meter = Meter.objects.get(serial_number=serial_number, is_active=True)
                
                # Generate token (format: XXXX-XXXX-XXXX-XXXX)
                token = '-'.join(
                    ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4)) 
                    for _ in range(4))
                
                # Calculate units (simple simulation: 100 RWF = 1 unit)
                units = amount / 100
                
                # Create purchase record
                purchase = PowerPurchase.objects.create(
                    meter=meter,
                    amount=amount,
                    token=token,
                    units=units,
                    purchase_date=timezone.now()
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Power purchase successful!',
                    'purchase_details': {
                        'token': token,
                        'units': units,
                        'amount': amount,
                        'date': purchase.purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'meter_number': meter.serial_number
                    }
                })
            except Meter.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Meter not found or inactive'
                }, status=400)
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'An error occurred: {str(e)}'
                }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    }, status=400)

@csrf_exempt
@meter_login_required
def check_power(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        serial_number = request.POST.get('serial_number')
        
        try:
            meter = Meter.objects.get(serial_number=serial_number, is_active=True)

            # Simulated values (replace with actual data if available)
            meter_info = {
                'owner_name': meter.name,
                'remaining_energy': round(random.uniform(10, 100), 2),  # in kWh
                'power': round(random.uniform(50, 500), 2),  # in Watts
                'unit_price': round(96.0, 2),  # per kWh (static or dynamic)
                'voltage': round(random.uniform(210, 250), 2),  # in Volts
                'current': round(random.uniform(1, 10), 2),  # in Amps
                'power_factor': round(random.uniform(0.7, 1.0), 2),
                'energy_consumed': round(random.uniform(50, 1000), 2),  # in kWh
            }

            return JsonResponse({'status': 'success', 'meter_info': meter_info})

        except Meter.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Meter not found or inactive'})
    
    return render(request, "energy_meter_client/check_power/check_power.html")

@meter_login_required
def update_profile(request):
    context = {}
    
    # Determine if user is Django user or meter user
    if request.user.is_authenticated:
        context['username'] = request.user.username
        context['is_django_user'] = True
        user_object = request.user
    elif request.session.get('is_meter_user', False):
        context['username'] = request.session.get('meter_username')
        context['is_django_user'] = False
        # Get the meter user object
        try:
            user_object = Meter.objects.get(username=context['username'])
        except Meter.DoesNotExist:
            messages.error(request, 'User account not found')
            return redirect('login')  # Redirect to login if user not found
    else:
        messages.error(request, 'You must be logged in to update your profile')
        return redirect('login')
    
    # Handle form submission
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validate username (not empty)
        if not username:
            messages.error(request, 'Username cannot be empty')
            return redirect('update_profile')
        
        # Check if username is taken by another user
        if username != context['username']:
            if context['is_django_user']:
                if User.objects.filter(username=username).exclude(id=user_object.id).exists():
                    messages.error(request, 'This username is already taken')
                    return redirect('update_profile')
            else:
                if Meter.objects.filter(username=username).exclude(id=user_object.id).exists():
                    messages.error(request, 'This username is already taken')
                    return redirect('update_profile')
        
        # Update username
        user_object.username = username
        
        # Update password if provided
        if password:
            if context['is_django_user']:
                user_object.set_password(password)
            else:
                user_object.password = make_password(password)
        
        # Save changes
        user_object.save()
        
        # Update session if username changed
        if username != context['username']:
            if context['is_django_user']:
                # Django users need to re-authenticate with new credentials
                messages.success(request, 'Profile updated successfully! Please log in with your new credentials')
                logout_view(request)
                return redirect('index')
            else:
                # Update meter user session
                request.session['meter_username'] = username
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('customer_service')  # Redirect to dashboard or appropriate page
    
    # Render the form with context
    return render(request, "energy_meter_client/forms/update_profile.html", context)
