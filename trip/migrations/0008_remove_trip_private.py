# Generated by Django 3.2.6 on 2021-10-03 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0007_trip_incomplete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='private',
        ),
    ]
