# Generated by Django 5.0.8 on 2024-11-23 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_tenantprofile_subscription_plan_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='landlordprofile',
            name='is_phone_verified',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='tenantprofile',
            name='is_phone_verified',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
