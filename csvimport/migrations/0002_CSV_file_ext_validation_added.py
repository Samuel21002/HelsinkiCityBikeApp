# Generated by Django 4.1.5 on 2023-01-12 19:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csvimport', '0001_Models_Initial_Create'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csv',
            name='file_name',
            field=models.FileField(upload_to='csv_uploads', validators=[django.core.validators.FileExtensionValidator(['csv'], 'The file must be a CSV-file!')]),
        ),
    ]
