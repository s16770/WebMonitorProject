# Generated by Django 2.2.17 on 2021-03-16 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0013_device_producent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='status',
            field=models.NullBooleanField(default=None, editable=False),
        ),
    ]
