# Generated by Django 2.2.17 on 2021-05-24 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0064_auto_20210524_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='producent',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='WebMonitor.Producent'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='firewall',
            name='producent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='WebMonitor.Producent'),
        ),
    ]
