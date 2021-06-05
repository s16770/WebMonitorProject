# Generated by Django 2.2.17 on 2021-06-05 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0066_auto_20210524_1221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='firewall',
            name='zones',
        ),
        migrations.AddField(
            model_name='zone',
            name='firewall',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='WebMonitor.Firewall'),
        ),
    ]
