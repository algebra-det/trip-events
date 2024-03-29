# Generated by Django 3.2.6 on 2021-09-21 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0020_booking_commission_at_time_of_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Cancelled By Host', 'Cancelled By Host'), ('Cancelled By User', 'Cancelled By User')], default='Pending', max_length=20),
        ),
    ]
