from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from . models import *
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
import random
import logging
import string
from functools import wraps
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date

def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember') == 'true'
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if not remember_me:
                request.session.set_expiry(0)  
            
            if user.is_superuser:
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('admin_dashboard')  
            else:
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('user_dashboard')  
        
        else:
            # Try to authenticate as a Meter client
            try:
                meter = Meter.objects.get(username=username)
                
                # Check password using the custom method in Meter model
                if meter.check_password(password):
                    # Successful Meter authentication
                    # Store meter info in session instead of using Django's auth system
                    request.session['meter_id'] = meter.id
                    request.session['meter_username'] = meter.username
                    request.session['meter_name'] = meter.name
                    request.session['is_meter_user'] = True
                    
                    if not remember_me:
                        request.session.set_expiry(0)
                    
                    messages.success(request, f"Welcome, {meter.name}!")
                    return redirect('customer_service')  
                else:
                    messages.error(request, "Invalid username or password")
            except Meter.DoesNotExist:
                messages.error(request, "Invalid username or password")
    
    return render(request, "energy_meter_app/forms/index.html")

# Example decorator for protecting meter client views
def meter_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Check for both meter users AND Django users (especially superusers)
        is_meter_user = request.session.get('is_meter_user', False)
        is_django_user = request.user.is_authenticated
        
        if not (is_meter_user or is_django_user):
            messages.error(request, "Please log in to access this page")
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapped_view

# Logout view for both Django users and meter users
def logout_view(request):
    # Handle Django user logout
    if request.user.is_authenticated:
        from django.contrib.auth import logout
        logout(request)
    
    # Handle meter user logout
    if 'meter_id' in request.session:
        del request.session['meter_id']
    if 'meter_username' in request.session:
        del request.session['meter_username']
    if 'meter_name' in request.session:
        del request.session['meter_name']
    if 'is_meter_user' in request.session:
        del request.session['is_meter_user']
    
    # Clear all session data
    request.session.flush()
    
    # Show logout message
    messages.success(request, "You have been logged out successfully")
    
    response = redirect('index')
    # Add cache-control headers to prevent back-button access
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

@meter_login_required
def dashboard(request):
    return render(request, "energy_meter_app/dashboards/admin_dashboard.html")

@meter_login_required
def add_meter(request):
    if request.method == 'POST':
        serial_number = request.POST.get('serial_number')
        national_id = request.POST.get('national_id')
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        status = request.POST.get('status', 'client')
        is_active = request.POST.get('is_active', 'True') == 'True'
        
        # Validate required fields
        if not all([serial_number, national_id, name, phone_number, address]):
            messages.error(request, 'All fields are required')
            return redirect('add_meter')
        
        # Check if meter with same serial number already exists
        if Meter.objects.filter(serial_number=serial_number).exists():
            messages.error(request, 'Meter with this serial number already exists')
            return redirect('add_meter')
        
        # Check if national ID already exists
        if Meter.objects.filter(national_id=national_id).exists():
            messages.error(request, 'User with this national ID already exists')
            return redirect('add_meter')
        
        # Check if phone number already exists
        if Meter.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'User with this phone number already exists')
            return redirect('add_meter')
        
        # Generate default username (first part of name + last 4 digits of national ID)
        first_name = name.split()[0].lower() if name.split() else ''
        username = f"{first_name}{national_id[-4:]}"
        
        # Check if username exists and make it unique if necessary
        original_username = username
        counter = 1
        while Meter.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Generate random password (8 characters)
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Create new meter
        try:
            meter = Meter(
                serial_number=serial_number,
                national_id=national_id,
                name=name,
                phone_number=phone_number,
                address=address,
                role=status,
                is_active=is_active,
                username=username,
                password=make_password(password)  # Hash the password
            )
            meter.save()
            
            # Show success message with generated credentials
            messages.success(
                request, 
                f'Meter added successfully! Default login credentials - Username: {username}, Password: {password}'
            )
            return redirect('manage_meters')  # Redirect to meter list page
            
        except Exception as e:
            messages.error(request, f'Error adding meter: {str(e)}')
            return redirect('add_meter')
    
    # If GET request, just render the form
    return render(request, "energy_meter_app/forms/add_meter.html")

@meter_login_required
def manage_meters(request):
    meters = Meter.objects.all()
    return render(request, "energy_meter_app/tables/manage_meter.html", {'meters': meters})

@meter_login_required
def update_meter(request, meter_id):
    if request.method == 'POST':
        meter = Meter.objects.get(id=meter_id)
        meter.serial_number = request.POST.get('serial_number')
        meter.national_id = request.POST.get('national_id')
        meter.name = request.POST.get('name')
        meter.phone_number = request.POST.get('phone_number')
        meter.address = request.POST.get('address')
        meter.role = request.POST.get('status')
        meter.is_active = request.POST.get('is_active') == 'True'
        meter.save()
        messages.success(request, 'Meter updated successfully')
        return redirect('manage_meters')
    else:
        meter = Meter.objects.get(id=meter_id)
        return render(request, "energy_meter_app/forms/update_meter.html", {'meter': meter})
    
@meter_login_required
def delete_meter(request, meter_id):
    if request.method == 'POST':
        try:
            meter = get_object_or_404(Meter, id=meter_id)
            
            serial_number = meter.serial_number
            
            meter.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Energy Meter with serial number {serial_number} has been deleted successfully.'
            })
            
        except Exception as e:
            logging.error(f"Error deleting meter {meter_id}: {str(e)}")
            
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while trying to delete the meter.'
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'This endpoint only accepts POST requests.'
        }, status=405)
    
@meter_login_required
def report_meters(request):
    show_table = False
    meters = []
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        try:
            # Parse the date strings to datetime objects
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            # Add one day to end_date to include the entire day
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            
            # Filter meters created between the start and end dates
            meters = Meter.objects.filter(
                created_at__gte=start_date_obj,
                created_at__lt=end_date_obj
            )
            
            show_table = True
            
            if not meters.exists():
                messages.info(request, "No meters found for the selected date range.")
        
        except Exception as e:
            messages.error(request, f"Error processing date range: {str(e)}")
    
    context = {
        'meters': meters,
        'show_table': show_table,
    }
    
    return render(request, "energy_meter_app/tables/report_meters.html", context)

@meter_login_required
def data_display(request):
    meters = Meter.objects.all() 
    return render(request, "energy_meter_app/data/data_display.html", {'meters': meters})


