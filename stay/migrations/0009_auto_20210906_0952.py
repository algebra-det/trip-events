# Generated by Django 3.2.6 on 2021-09-06 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stay', '0008_alter_stayimage_stay'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facilities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='stay',
            name='stay_type',
            field=models.CharField(choices=[('Home Stay', 'Home Stay'), ('Hostel', 'Hostel'), ('Camp Site', 'Camp Site'), ('GLAMPING', 'GLAMPING'), ('OffBeat', 'OffBeat'), ('TreeHouse', 'TreeHouse'), ('House Boats', 'House Boats'), ('Farm Stay', 'Farm Stay'), ('Tiny House', 'Tiny House'), ('Others', 'Others')], max_length=50),
        ),
    ]
