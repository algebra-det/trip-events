# Generated by Django 3.2.6 on 2021-09-08 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_auto_20210904_0735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temptoken',
            name='usage',
            field=models.CharField(choices=[('Password', 'Password'), ('Email', 'Email'), ('Profile', 'Profile'), ('Travel Type', 'Travel Type'), ('Trip Interest', 'Trip Interest'), ('Wander List', 'Wander List')], default='Password', max_length=20),
        ),
    ]
