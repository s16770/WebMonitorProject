# Generated by Django 2.2.17 on 2021-03-16 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0014_auto_20210316_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='status',
            field=models.NullBooleanField(editable=False),
        ),
    ]