# Generated by Django 3.2.6 on 2021-09-27 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0006_rename_number_of_travelers_trip_number_of_travellers'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='incomplete',
            field=models.BooleanField(default=True),
        ),
    ]
