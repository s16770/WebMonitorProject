# Generated by Django 2.2.17 on 2021-03-14 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0003_device_community_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Producent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('status_osOID', models.CharField(max_length=50)),
                ('status_opOID', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='device',
            name='producent',
        ),
    ]
