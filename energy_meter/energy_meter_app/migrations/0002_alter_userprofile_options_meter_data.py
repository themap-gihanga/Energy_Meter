# Generated by Django 5.1.2 on 2024-10-29 15:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy_meter_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'ordering': ['created_at'], 'verbose_name': 'User Profile', 'verbose_name_plural': 'User Profiles'},
        ),
        migrations.CreateModel(
            name='Meter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=30, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='energy_meter_app.userprofile')),
            ],
            options={
                'verbose_name': 'Meter',
                'verbose_name_plural': 'Meters',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voltage', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current', models.DecimalField(decimal_places=2, max_digits=10)),
                ('energy', models.DecimalField(decimal_places=2, max_digits=10)),
                ('power_factor', models.DecimalField(decimal_places=2, max_digits=5)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('serial_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_records', to='energy_meter_app.meter')),
            ],
            options={
                'verbose_name': 'Data',
                'verbose_name_plural': 'Data Records',
                'ordering': ['created_at'],
            },
        ),
    ]
