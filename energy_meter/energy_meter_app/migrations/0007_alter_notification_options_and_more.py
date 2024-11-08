# Generated by Django 5.1.2 on 2024-11-01 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy_meter_app', '0006_notification'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('INSERT', 'New Record Added'), ('UPDATE', 'Record Updated'), ('DELETE', 'Record Deleted'), ('DOWNLOAD', 'Data Downloaded'), ('OTHER', 'Other Action')], default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='related_object',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
