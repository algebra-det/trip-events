# Generated by Django 3.2.6 on 2021-09-02 09:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_auto_20210831_1127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='accepted',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='from_date',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='to_date',
        ),
        migrations.AddField(
            model_name='event',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]