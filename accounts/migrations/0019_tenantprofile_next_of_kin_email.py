# Generated by Django 5.0.8 on 2024-12-03 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_tenantprofile_next_of_kin_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantprofile',
            name='next_of_kin_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
