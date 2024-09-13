# Generated by Django 5.0.8 on 2024-09-12 21:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_tenantprofile_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PricingTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('max_properties', models.IntegerField(blank=True, null=True)),
                ('max_property_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('target', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tenantprofile',
            name='num_properties',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tenantprofile',
            name='pricing_tier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.pricingtier'),
        ),
    ]
