# Generated by Django 3.2.6 on 2021-08-31 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='price_of_trip',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
