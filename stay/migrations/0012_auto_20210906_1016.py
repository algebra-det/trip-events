# Generated by Django 3.2.6 on 2021-09-06 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stay', '0011_nearesthotspots'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stay',
            name='nearby',
        ),
        migrations.AlterField(
            model_name='nearesthotspots',
            name='stay',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nearby', to='stay.stay'),
        ),
    ]
