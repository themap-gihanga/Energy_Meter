from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Meter

def meter_auth_middleware(get_response):
    def middleware(request):
        # Paths that should be accessible without authentication
        public_paths = [
            reverse('index'),  # Login page
            '/static/',        # Static files
            '/media/',         # Media files
            # Add any other public paths here
        ]
        
        # Check if the current path is in public paths
        is_public_path = any(request.path.startswith(path) for path in public_paths)
        
        # Check user authentication status
        is_django_user = request.user.is_authenticated
        is_superuser = request.user.is_authenticated and request.user.is_superuser
        is_meter_user = request.session.get('is_meter_user', False)
        meter_id = request.session.get('meter_id')
        
        # If user is not authenticated and trying to access a protected page
        if not (is_django_user or is_meter_user) and not is_public_path:
            messages.warning(request, "Please login to access this page")
            return redirect('index')
        
        # For authenticated meter users, add current_meter to request
        if is_meter_user and meter_id:
            try:
                request.current_meter = Meter.objects.get(id=meter_id)
            except Meter.DoesNotExist:
                # Clear invalid session data
                if 'meter_id' in request.session:
                    del request.session['meter_id']
                if 'meter_username' in request.session:
                    del request.session['meter_username']
                if 'meter_name' in request.session:
                    del request.session['meter_name']
                if 'is_meter_user' in request.session:
                    del request.session['is_meter_user']
                
                # Redirect to login page if meter doesn't exist anymore
                messages.error(request, "Your session has expired. Please login again.")
                return redirect('index')
        
        # For superusers, set a flag that can be checked in views
        if is_superuser:
            request.is_superuser = True
            # You could also set session data for superusers if needed
            request.session['is_superuser'] = True
        
        # Continue with the request if everything is fine
        response = get_response(request)
        
        # Add security headers to prevent caching of authenticated pages
        if not is_public_path:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
    return middleware