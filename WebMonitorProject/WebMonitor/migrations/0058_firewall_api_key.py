# Generated by Django 2.2.17 on 2021-05-16 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0057_auto_20210504_0103'),
    ]

    operations = [
        migrations.AddField(
            model_name='firewall',
            name='api_key',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
