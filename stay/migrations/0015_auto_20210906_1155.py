# Generated by Django 3.2.6 on 2021-09-06 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stay', '0014_alter_nearesthotspots_stay'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stay',
            name='facilities',
        ),
        migrations.AddField(
            model_name='stay',
            name='facilities',
            field=models.ManyToManyField(default=None, related_name='stays', to='stay.Facility'),
        ),
    ]
