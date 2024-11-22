from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout  
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from . models import *
from django.db import IntegrityError
from django.utils import timezone
import datetime

def get_user_dashboard(user):
    if user.is_superuser:
        return 'admin_dashboard'
    try:
        user_profile = UserProfile.objects.get(name=user.username)
        if user_profile.status == 'staff':
            return 'staff_dashboard'
        elif user_profile.status == 'client':
            return 'client_dashboard'
    except UserProfile.DoesNotExist:
        return 'login_users'
    return 'login_users'

def login_users(request):
    if request.user.is_authenticated:
        dashboard = get_user_dashboard(request.user)
        return redirect(dashboard)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            dashboard = get_user_dashboard(user)
            return redirect(dashboard)
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login_users')
        
    return render(request, 'energy_meter_app/forms/login_users.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect(get_user_dashboard(request.user))

    now = timezone.now()
    
    # Get filter parameters for each card
    meter_filter = request.GET.get('meter_filter', 'all')
    user_filter = request.GET.get('user_filter', 'all')
    data_filter = request.GET.get('data_filter', 'all')

    # Function to get date range based on filter type
    def get_date_range(filter_type):
        if filter_type == 'today':
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif filter_type == 'this_month':
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif filter_type == 'this_year':
            return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return None

    # Get counts for meters
    meter_start_date = get_date_range(meter_filter)
    meter_query = Meter.objects.all()
    if meter_start_date:
        meter_query = meter_query.filter(created_at__gte=meter_start_date)
    total_meters = meter_query.count()

    # Get counts for users
    user_start_date = get_date_range(user_filter)
    user_query = UserProfile.objects.all()
    if user_start_date:
        user_query = user_query.filter(created_at__gte=user_start_date)
    total_users = user_query.count()

    # Get counts for data entries
    data_start_date = get_date_range(data_filter)
    data_query = Data.objects.all()
    if data_start_date:
        data_query = data_query.filter(created_at__gte=data_start_date)
    total_data_entries = data_query.count()

    context = {
        'dashboard_type': 'Admin',
        'total_meters': total_meters,
        'total_users': total_users,
        'total_data_entries': total_data_entries,
        'meter_filter': meter_filter,
        'user_filter': user_filter,
        'data_filter': data_filter,
    }

    return render(request, 'energy_meter_app/dashboards/admin_dashboard.html', context)
        
@login_required
def staff_dashboard(request):
    try:
        user_profile = UserProfile.objects.get(name=request.user.username)
        if user_profile.status != 'staff':
            return redirect(get_user_dashboard(request.user))
    except UserProfile.DoesNotExist:
        return redirect('index_page')
    
    context = {
        'dashboard_type': 'Staff',
        'user_profile': user_profile
    }
    return render(request, 'energy_meter_app/dashboards/staff_dashboard.html', context)

@login_required
def client_dashboard(request):
    try:
        user_profile = UserProfile.objects.get(name=request.user.username)
        if user_profile.status != 'client':
            return redirect(get_user_dashboard(request.user))
    except UserProfile.DoesNotExist:
        return redirect('index_page')
    
    context = {
        'dashboard_type': 'Client',
        'user_profile': user_profile
    }
    return render(request, 'energy_meter_app/dashboards/client_dashboard.html', context)

@login_required
def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out")
    return redirect('login_users')

@login_required
def add_user_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        national_id = request.POST.get('national_id')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        status = request.POST.get('role')  

        try:
            user_profile = UserProfile(
                name=name,
                national_id=national_id,
                phone_number=phone_number,
                address=address,
                status=status  
            )
            user_profile.save()
            messages.success(request, "User added successfully.")
            return redirect('add_user')
          
        except Exception as e:
            messages.error(request, f"Error adding user: {e}")

    return render(request, 'energy_meter_app/forms/add_user.html')

@login_required
def manage_users_view(request):
    users = UserProfile.objects.all()  
    return render(request, 'energy_meter_app/tables/manage_users.html', {'users': users})

@login_required
def activate_user(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, "User Now Active.")
    return redirect('manage_users')

@login_required
def deactivate_user(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    user.is_active = False
    messages.success(request, "User Now Inactive.")
    user.save()
    return redirect('manage_users')

@login_required
def update_user_view(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.national_id = request.POST.get('national_id')
        user.phone_number = request.POST.get('phone_number')
        user.address = request.POST.get('address')
        user.status = request.POST.get('role')  
        user.save()
        messages.success(request, "User Successfully updated.") 
        return redirect('manage_users')  

    context = {
        'user': user
    }
    return render(request, 'energy_meter_app/forms/update_users.html', context)

@login_required
@require_POST
@ensure_csrf_cookie
def delete_user(request, user_id):
    try:
        user = get_object_or_404(UserProfile, id=user_id)
        
        if not request.user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': "You don't have permission to delete users."
            }, status=403)
        
        user_name = user.name
        
        try:
            user.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f"User {user_name} has been successfully deleted."
            })
            
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': "Failed to delete user. Please try again."
            }, status=500)
            
    except Exception as e:
        print(f"Error in delete_user view: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': "An error occurred while processing your request."
        }, status=500)
    
@login_required
def report_users_view(request):
    users = None  
    show_table = False  

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if start_date and end_date:
            start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))

            end_date = end_date.replace(hour=23, minute=59, second=59)

            users = UserProfile.objects.filter(created_at__range=[start_date, end_date])
            show_table = True  

    return render(request, 'energy_meter_app/tables/report_users.html', {'users': users, 'show_table': show_table})

@login_required
def add_meter(request):
    userprofiles = UserProfile.objects.all()
    
    if request.method == "POST":
        serial_number = request.POST.get("serial_number")
        national_id = request.POST.get("national_id")

        # Get or create the UserProfile
        owner_profile, created = UserProfile.objects.get_or_create(national_id=national_id)
        
        # Update or set UserProfile fields
        owner_profile.name = request.POST.get("name", owner_profile.name)  # Keep existing name if not provided
        owner_profile.phone_number = request.POST.get("phone_number", owner_profile.phone_number)
        owner_profile.address = request.POST.get("address", owner_profile.address)
        owner_profile.status = request.POST.get("role", owner_profile.status)
        owner_profile.save()  # Save changes
        
        try:
            # Create the Meter
            Meter.objects.create(serial_number=serial_number, owner=owner_profile)
            messages.success(request, "Meter added successfully.")
            return redirect("add_meter")
        
        except IntegrityError:
            messages.error(request, "A meter with this serial number already exists.")
            return redirect("add_meter")
    
    return render(request, "energy_meter_app/forms/add_meter.html", {"userprofiles": userprofiles})

@login_required
def manage_meter(request):
    meters = Meter.objects.all()  
    return render(request, 'energy_meter_app/tables/manage_meter.html', {'meters': meters})

@login_required
@require_POST
@ensure_csrf_cookie
def delete_meter(request, meter_id):
    try:
        meter = get_object_or_404(Meter, id=meter_id)
        
        if not request.user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': "You don't have permission to delete meter."
            }, status=403)
        
        meter_name = meter.serial_number
        
        try:
            meter.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f"Energy Meter {meter_name} has been successfully deleted."
            })
            
        except Exception as e:
            print(f"Error deleting Energy Meter: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': "Failed to delete user. Please try again."
            }, status=500)
            
    except Exception as e:
        print(f"Error in delete_meter view: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': "An error occurred while processing your request."
        }, status=500)

@login_required
def update_meter(request, meter_id):
    meter = get_object_or_404(Meter, id=meter_id)
    user = meter.owner  

    if request.method == 'POST':
        try:
            meter.serial_number = request.POST.get('serial_number')
            meter.save()  

            user.name = request.POST.get('name')
            user.national_id = request.POST.get('national_id')
            user.phone_number = request.POST.get('phone_number')
            user.address = request.POST.get('address')
            user.status = request.POST.get('role')
            user.save()  

            messages.success(request, 'Meter and user information updated successfully!')
            return redirect('manage_meter')

        except IntegrityError:
            messages.error(request, 'The National ID entered is already in use by another user. Please try a different one.')
            
    return render(request, 'energy_meter_app/forms/update_meter.html', {'meter': meter, 'user': user})

@login_required
def report_meters_view(request):
    meters = None  
    show_table = False  

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if start_date and end_date:
            start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))

            end_date = end_date.replace(hour=23, minute=59, second=59)

            meters = Meter.objects.filter(created_at__range=[start_date, end_date])
            show_table = True  

    return render(request, 'energy_meter_app/tables/report_meters.html', {'meters': meters, 'show_table': show_table})

@login_required
def add_data(request):
    meters = Meter.objects.all()

    if request.method == "POST":
        serial_number = request.POST.get("serial_number")
        voltage = float(request.POST.get("voltage", 0))
        current = float(request.POST.get("current", 0))
        energy = float(request.POST.get("energy", 0))
        power_factor = float(request.POST.get("power_factor", 1))
        unit_price = request.POST.get("unit_price")

        # Calculate power if needed
        power = voltage * current * power_factor  # Or adjust formula as needed

        try:
            serial_meter = Meter.objects.get(serial_number=serial_number)
        except Meter.DoesNotExist:
            messages.error(request, "The meter with this serial number does not exist. Please register the meter first.")
            return redirect("add_data")

        try:
            Data.objects.create(
                voltage=voltage,
                current=current,
                energy=energy,
                power_factor=power_factor,
                unit_price=unit_price,
                serial_number=serial_meter,
                power=power,  # Ensure `power` is saved here if it's in the model
            )
            messages.success(request, "Data added successfully.")
            return redirect("add_data")

        except IntegrityError as e:
            messages.error(request, f"An error occurred while adding data: {e}")
            return redirect("add_data")

    context = {
        'meters': meters,
    }
    return render(request, "energy_meter_app/forms/add_data.html", context)

@login_required
def get_meter_data(request, serial_number):
    try:
        # Fetch the latest data entry for the selected meter
        meter = Meter.objects.get(serial_number=serial_number)
        latest_data = Data.objects.filter(serial_number=meter).order_by('-timestamp').first()

        if latest_data:
            data = {
                'voltage': latest_data.voltage,
                'current': latest_data.current,
                'energy': latest_data.energy,
                'power_factor': latest_data.power_factor,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'No data found for this meter'}, status=404)
    except Meter.DoesNotExist:
        return JsonResponse({'error': 'Meter not found'}, status=404)
    
@login_required
def manage_data(request):
    datas = Data.objects.all()  
    return render(request, 'energy_meter_app/tables/manage_data.html', {'datas': datas})

@login_required
def update_data(request, data_id):
    data = get_object_or_404(Data, id=data_id)  # Use your actual model name

    if request.method == "POST":
        # Update your fields accordingly
        data.voltage = float(request.POST.get("voltage", 0))
        data.current = float(request.POST.get("current", 0))
        data.energy = float(request.POST.get("energy", 0))
        data.power_factor = float(request.POST.get("power_factor", 1))
        data.unit_price = request.POST.get("unit_price")

        try:
            data.save()
            messages.success(request, "Meter data updated successfully.")
            return redirect("manage_data")  # Redirect to your manage data page

        except IntegrityError as e:
            messages.error(request, f"An error occurred while updating data: {e}")
            return redirect("manage_data")

    context = {
        'data': data,  # Ensure you're passing the correct context
    }
    return render(request, "energy_meter_app/forms/update_data.html", context)

@login_required
@require_POST
@ensure_csrf_cookie
def delete_data(request, data_id):
    try:
        data = get_object_or_404(Data, id=data_id)
        if not request.user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': "You don't have permission to delete this data."
            }, status=403)

        data.delete()
        return JsonResponse({
            'status': 'success',
            'message': f"Data for Energy Meter has been successfully deleted."
        })

    except Exception as e:
        print(f"Error in delete_data view: {e}")
        return JsonResponse({
            'status': 'error',
            'message': "An error occurred while processing your request."
        }, status=500)


@login_required
def report_data_view(request):
    datas = None
    show_table = False
    
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if start_date and end_date:
            start_date = timezone.make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d'))
            end_date = end_date.replace(hour=23, minute=59, second=59)
            
            datas = Data.objects.filter(created_at__range=[start_date, end_date])
            show_table = True
    
    return render(request, 'energy_meter_app/tables/report_data.html', {
        'datas': datas,
        'show_table': show_table
    })