# Generated by Django 2.2.17 on 2021-05-03 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0055_auto_20210504_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='start_time',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
