from django.contrib import admin
from .models import *


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'national_id', 'phone_number', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('name', 'national_id', 'phone_number')
    ordering = ['created_at']
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'is_active')

admin.site.register(UserProfile, UserProfileAdmin)

class MeterAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'owner', 'created_at', 'updated_at')
    search_fields = ('serial_number',)  
    list_filter = ('owner',)  
    ordering = ['created_at']

admin.site.register(Meter, MeterAdmin)

class AdminData(admin.ModelAdmin):
    list_display = ('serial_number', 'voltage', 'current', 'energy', 'power_factor', 'unit_price', 'created_at')
    search_fields = ('serial_number__serial_number',)  
    list_filter = ('serial_number__owner',)  
    ordering = ['created_at']

admin.site.register(Data, AdminData)


