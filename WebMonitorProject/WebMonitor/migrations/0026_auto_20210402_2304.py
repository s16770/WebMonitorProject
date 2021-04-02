# Generated by Django 2.2.17 on 2021-04-02 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0025_session_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='free_storage',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='storage',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='producent',
            name='freestorage_opOID',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='producent',
            name='freestorage_osOID',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
