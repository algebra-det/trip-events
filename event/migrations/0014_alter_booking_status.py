# Generated by Django 3.2.6 on 2021-09-15 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0013_auto_20210915_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], max_length=20),
        ),
    ]