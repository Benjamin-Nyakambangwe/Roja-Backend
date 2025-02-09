# Generated by Django 5.0.8 on 2025-01-07 17:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_property_overall_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='property',
            options={'ordering': ['-overall_rating', '-id']},
        ),
        migrations.AddIndex(
            model_name='property',
            index=models.Index(fields=['-overall_rating'], name='api_propert_overall_e1f28c_idx'),
        ),
    ]
