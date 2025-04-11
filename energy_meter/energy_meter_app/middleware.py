# energy_meter_app/middleware.py

from django.utils.deprecation import MiddlewareMixin
from energy_meter_app.models import UserProfile

class StaffAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # If user is not authenticated via User but session has staff info
        if not request.user.is_authenticated and 'user_status' in request.session:
            if request.session['user_status'] == 'staff':
                try:
                    request.user_profile = UserProfile.objects.get(id=request.session['user_profile_id'])
                except UserProfile.DoesNotExist:
                    request.user_profile = None
