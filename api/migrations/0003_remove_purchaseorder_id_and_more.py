# Generated by Django 5.0 on 2023-12-09 17:30

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_vendor_average_response_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorder',
            name='id',
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='po_number',
            field=models.CharField(default=api.models.create_new_odr_number, max_length=10, primary_key=True, serialize=False, unique=True),
        ),
    ]
