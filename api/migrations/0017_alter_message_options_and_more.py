# Generated by Django 5.0.8 on 2024-10-20 08:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_property_current_tenant'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['timestamp']},
        ),
        migrations.RemoveIndex(
            model_name='message',
            name='api_message_sender__7d2c6a_idx',
        ),
        migrations.RemoveIndex(
            model_name='message',
            name='api_message_receive_d51b26_idx',
        ),
        migrations.RemoveIndex(
            model_name='message',
            name='api_message_timesta_d1f903_idx',
        ),
        migrations.AddField(
            model_name='property',
            name='previous_tenants',
            field=models.ManyToManyField(blank=True, related_name='previous_tenants', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='property',
            name='previous_tenants_with_access',
            field=models.ManyToManyField(blank=True, related_name='previous_tenants_with_access', to=settings.AUTH_USER_MODEL),
        ),
    ]
