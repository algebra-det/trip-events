# Generated by Django 3.2.6 on 2021-09-06 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stay', '0015_auto_20210906_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stay',
            name='facilities',
            field=models.ManyToManyField(blank=True, default=None, related_name='stays', to='stay.Facility'),
        ),
    ]
