# Generated by Django 2.2.17 on 2021-05-03 10:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0051_auto_20210502_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='category',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='session',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 3, 12, 46, 51, 315312)),
        ),
    ]
