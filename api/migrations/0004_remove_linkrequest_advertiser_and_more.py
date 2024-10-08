# Generated by Django 5.0.8 on 2024-08-24 09:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_site_casino_multiplier_site_crypto_multiplier_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='linkrequest',
            name='advertiser',
        ),
        migrations.RemoveField(
            model_name='linkrequest',
            name='site',
        ),
        migrations.RemoveField(
            model_name='linkrequest',
            name='status',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='request',
        ),
        migrations.RemoveField(
            model_name='site',
            name='niche',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='advertiser',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='publisher',
        ),
        migrations.RemoveField(
            model_name='report',
            name='advertiser',
        ),
        migrations.RemoveField(
            model_name='report',
            name='publisher',
        ),
        migrations.RemoveField(
            model_name='site',
            name='publisher',
        ),
        migrations.DeleteModel(
            name='LinkRequestStatus',
        ),
        migrations.DeleteModel(
            name='LinkRequest',
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
        migrations.DeleteModel(
            name='Niche',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
        migrations.DeleteModel(
            name='Report',
        ),
        migrations.DeleteModel(
            name='Site',
        ),
    ]
