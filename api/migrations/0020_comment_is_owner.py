# Generated by Django 5.0.8 on 2024-10-27 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_remove_comment_api_comment_tenant__4ae6d5_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_owner',
            field=models.BooleanField(default=False),
        ),
    ]
