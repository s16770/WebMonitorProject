# Generated by Django 2.2.17 on 2021-05-02 18:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0049_auto_20210502_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 2, 20, 30, 29, 448496)),
        ),
    ]
