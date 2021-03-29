# Generated by Django 2.2.17 on 2021-03-29 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WebMonitor', '0022_producent_services'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_ip', models.CharField(max_length=20)),
                ('application', models.CharField(max_length=30)),
                ('transfer', models.PositiveIntegerField()),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WebMonitor.Device')),
                ('source_zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WebMonitor.Zone')),
            ],
        ),
    ]
