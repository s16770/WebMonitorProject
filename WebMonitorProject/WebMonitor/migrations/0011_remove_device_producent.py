# Generated by Django 2.2.17 on 2021-03-15 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0010_auto_20210315_1743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='producent',
        ),
    ]
