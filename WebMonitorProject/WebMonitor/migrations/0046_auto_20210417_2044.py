# Generated by Django 2.2.17 on 2021-04-17 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0045_auto_20210416_1824'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='transfer_opOID',
        ),
        migrations.RemoveField(
            model_name='device',
            name='transfer_osOID',
        ),
    ]
