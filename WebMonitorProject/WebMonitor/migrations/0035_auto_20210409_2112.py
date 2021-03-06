# Generated by Django 2.2.17 on 2021-04-09 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0034_auto_20210407_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='cpu_load',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='temperature',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10, null=True),
        ),
    ]
