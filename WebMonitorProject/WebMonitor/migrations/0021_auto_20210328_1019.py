# Generated by Django 2.2.17 on 2021-03-28 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0020_device_nat_ipaddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('port', models.PositiveIntegerField()),
                ('service_osOID', models.CharField(max_length=50, null=True)),
                ('service_opOID', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='producent',
            name='storage_opOID',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='producent',
            name='storage_osOID',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='producent',
            name='temperature_opOID',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='producent',
            name='temperature_osOID',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='producent',
            name='transfer_opOID',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='producent',
            name='transfer_osOID',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
