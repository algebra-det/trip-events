# Generated by Django 3.2.6 on 2021-09-01 10:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20210901_0745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='sign_up_steps',
            field=models.CharField(choices=[('OTP Sent', 'OTP Sent'), ('OTP Verified', 'OTP Verified'), ('Password Set', 'Password Set'), ('Email Set', 'Email Set'), ('Travel Type Set', 'Travel Type Set'), ('Travel Interest Set', 'Travel Interest Set'), ('Wander List Set', 'Wander List Set'), ('Profile Added', 'Profile Added')], default='OTP Sent', max_length=20),
        ),
        migrations.AlterField(
            model_name='temptoken',
            name='token',
            field=models.CharField(default=uuid.uuid4, max_length=100),
        ),
    ]
