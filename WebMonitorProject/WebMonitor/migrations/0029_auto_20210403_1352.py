# Generated by Django 2.2.17 on 2021-04-03 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0028_auto_20210403_1349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producent',
            name='usedstorage_alloc_opOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='usedstorage_alloc_osOID',
        ),
    ]
