# Generated by Django 2.2.17 on 2021-05-02 18:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0048_session_alert_couse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 2, 20, 27, 0, 856538)),
        ),
    ]
