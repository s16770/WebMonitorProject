# Generated by Django 2.2.17 on 2021-03-27 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0019_auto_20210327_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='nat_ipaddress',
            field=models.GenericIPAddressField(null=True),
        ),
    ]
