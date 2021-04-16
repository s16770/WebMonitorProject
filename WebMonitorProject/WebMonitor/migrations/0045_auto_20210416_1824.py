# Generated by Django 2.2.17 on 2021-04-16 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0044_alert_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='used_storage_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]