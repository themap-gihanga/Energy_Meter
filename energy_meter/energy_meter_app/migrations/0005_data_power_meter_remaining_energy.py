# Generated by Django 5.1.2 on 2024-10-31 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy_meter_app', '0004_alter_meter_serial_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='power',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meter',
            name='remaining_energy',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
