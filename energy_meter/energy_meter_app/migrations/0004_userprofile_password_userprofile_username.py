# Generated by Django 5.1.2 on 2024-11-22 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy_meter_app', '0003_remove_userprofile_default_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]
