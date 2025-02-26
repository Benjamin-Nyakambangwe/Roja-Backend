# Generated by Django 5.0.8 on 2025-02-09 08:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_leasedocumentpayment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='leasedocumentpayment',
            options={},
        ),
        migrations.RemoveIndex(
            model_name='leasedocumentpayment',
            name='api_leasedo_propert_7fde51_idx',
        ),
        migrations.RemoveIndex(
            model_name='leasedocumentpayment',
            name='api_leasedo_status_6f076f_idx',
        ),
        migrations.AddField(
            model_name='leasedocumentpayment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='leasedocumentpayment',
            name='landlord',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='leasedocumentpayment',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.property'),
        ),
        migrations.AlterField(
            model_name='leasedocumentpayment',
            name='status',
            field=models.CharField(default='PENDING', max_length=20),
        ),
    ]
