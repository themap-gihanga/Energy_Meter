from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

class Meter(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
    ]
    serial_number = models.CharField(max_length=30, unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    
    # New fields for staff username and password
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Meter'
        verbose_name_plural = 'Meters'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} - {self.national_id}"
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    
class PowerPurchase(models.Model):
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='purchases')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    token = models.CharField(max_length=20, unique=True)
    units = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    # Additional useful fields
    status = models.CharField(max_length=20, default='completed', choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    
    class Meta:
        ordering = ['-purchase_date']
        verbose_name = 'Power Purchase'
        verbose_name_plural = 'Power Purchases'
    
    def __str__(self):
        return f"{self.meter.serial_number} - {self.token} - {self.amount}RWF"
