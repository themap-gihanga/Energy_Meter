
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    STATUS_CHOICES = [
        ('staff', 'Staff'),
        ('client', 'Client'),
    ]
    
    name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='client')
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} - {self.national_id}"

class Meter(models.Model):
    serial_number = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    remaining_energy = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  

    class Meta:
        verbose_name = 'Meter'
        verbose_name_plural = 'Meters'
        ordering = ['created_at']

    def __str__(self):
        return f"Meter {self.serial_number} - Owned by {self.owner.name}"
class Data(models.Model):
    serial_number = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='data_records')
    
    # Sensor Readings
    voltage = models.DecimalField(max_digits=10, decimal_places=2)  # Voltage in volts
    current = models.DecimalField(max_digits=10, decimal_places=2)  # Current in amperes
    power = models.DecimalField(max_digits=10, decimal_places=2)    # Power in watts
    energy = models.DecimalField(max_digits=10, decimal_places=2)   # Energy in kWh
    power_factor = models.DecimalField(max_digits=5, decimal_places=2)  # Power factor (dimensionless)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Timestamps for when the data is recorded
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        verbose_name = 'Data'
        verbose_name_plural = 'Data Records'
        ordering = ['created_at']

    def __str__(self):
        return f"Data for Meter {self.serial_number.serial_number} - Voltage: {self.voltage}V, Current: {self.current}A"


