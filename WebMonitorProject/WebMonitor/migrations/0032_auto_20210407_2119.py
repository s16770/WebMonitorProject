# Generated by Django 2.2.17 on 2021-04-07 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0031_auto_20210403_2211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producent',
            name='services',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='status_opOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='status_osOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='storage_alloc_opOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='storage_alloc_osOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='storage_opOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='storage_osOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='temperature_opOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='temperature_osOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='transfer_opOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='transfer_osOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='usedstorage_opOID',
        ),
        migrations.RemoveField(
            model_name='producent',
            name='usedstorage_osOID',
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_osOID', models.CharField(max_length=50)),
                ('status_opOID', models.CharField(max_length=50)),
                ('transfer_osOID', models.CharField(blank=True, max_length=50, null=True)),
                ('transfer_opOID', models.CharField(blank=True, max_length=50, null=True)),
                ('temperature_osOID', models.CharField(blank=True, max_length=50, null=True)),
                ('temperature_opOID', models.CharField(blank=True, max_length=50, null=True)),
                ('cpu_osOID', models.CharField(blank=True, max_length=50, null=True)),
                ('cpu_opOID', models.CharField(blank=True, max_length=50, null=True)),
                ('storage_osOID', models.CharField(blank=True, max_length=50, null=True)),
                ('storage_opOID', models.CharField(blank=True, max_length=50, null=True)),
                ('storage_alloc_osOID', models.CharField(blank=True, max_length=50, null=True)),
                ('storage_alloc_opOID', models.CharField(blank=True, max_length=50, null=True)),
                ('usedstorage_osOID', models.CharField(blank=True, max_length=50, null=True)),
                ('usedstorage_opOID', models.CharField(blank=True, max_length=50, null=True)),
                ('prod', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='WebMonitor.Producent')),
                ('services', models.ManyToManyField(blank=True, null=True, to='WebMonitor.Service')),
            ],
        ),
    ]
