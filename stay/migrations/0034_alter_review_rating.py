# Generated by Django 3.2.6 on 2021-09-13 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stay', '0033_auto_20210913_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1),
        ),
    ]
