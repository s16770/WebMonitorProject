# Generated by Django 2.2.17 on 2021-04-12 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0042_device_used_storage_percentage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=180)),
                ('timestamp', models.DateTimeField()),
                ('device', models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='WebMonitor.Device')),
            ],
        ),
    ]