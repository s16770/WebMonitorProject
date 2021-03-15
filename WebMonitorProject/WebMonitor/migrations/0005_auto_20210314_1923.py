# Generated by Django 2.2.17 on 2021-03-14 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0004_auto_20210314_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='producent',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='WebMonitor.Producent'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='device',
            name='sessions',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]