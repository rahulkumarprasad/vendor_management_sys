# Generated by Django 5.0 on 2023-12-11 04:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_purchaseorder_expected_delivery_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='expected_delivery_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 11, 4, 29, 51, 571488, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]