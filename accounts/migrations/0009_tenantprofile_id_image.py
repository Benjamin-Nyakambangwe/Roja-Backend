# Generated by Django 5.0.8 on 2024-09-10 04:42

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_remove_landlordprofile_handles_own_maintenance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantprofile',
            name='id_image',
            field=models.ImageField(blank=True, null=True, upload_to=accounts.models.upload_to),
        ),
    ]
