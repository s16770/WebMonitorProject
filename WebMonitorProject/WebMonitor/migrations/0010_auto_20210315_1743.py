# Generated by Django 2.2.17 on 2021-03-15 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0009_auto_20210315_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='producent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='WebMonitor.Producent'),
        ),
    ]
