# Generated by Django 3.2.6 on 2021-09-17 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0018_rename_total_pay_booking_paid_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='paid_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20),
        ),
    ]