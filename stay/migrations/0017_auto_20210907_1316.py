# Generated by Django 3.2.6 on 2021-09-07 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stay', '0016_alter_stay_facilities'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='from_date',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='to_date',
            new_name='start_date',
        ),
    ]
