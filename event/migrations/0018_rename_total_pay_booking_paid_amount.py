# Generated by Django 3.2.6 on 2021-09-17 08:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0017_booking_total_pay'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='total_pay',
            new_name='paid_amount',
        ),
    ]