# Generated by Django 5.1.2 on 2024-11-22 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('energy_meter_app', '0002_userprofile_default_password_userprofile_password_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='default_password',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='password',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='password_changed',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='username',
        ),
    ]
