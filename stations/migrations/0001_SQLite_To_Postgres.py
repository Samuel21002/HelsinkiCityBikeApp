# Generated by Django 4.1.5 on 2023-01-23 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('station_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('fid', models.BigIntegerField(unique=True)),
                ('name_fin', models.CharField(max_length=30)),
                ('name_swe', models.CharField(max_length=30)),
                ('name_eng', models.CharField(default='', max_length=30)),
                ('address_fin', models.CharField(max_length=40)),
                ('address_swe', models.CharField(max_length=40)),
                ('city_fin', models.CharField(max_length=30, null=True)),
                ('city_swe', models.CharField(max_length=30, null=True)),
                ('operator', models.CharField(max_length=30, null=True)),
                ('capacity', models.PositiveSmallIntegerField(null=True)),
                ('geo_pos_x', models.DecimalField(decimal_places=6, max_digits=8)),
                ('geo_pos_y', models.DecimalField(decimal_places=6, max_digits=8)),
            ],
        ),
    ]
