# Generated by Django 3.2.6 on 2021-09-09 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stay', '0022_auto_20210909_0847'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='text',
        ),
    ]
