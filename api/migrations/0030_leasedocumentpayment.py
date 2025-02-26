# Generated by Django 5.0.8 on 2025-02-09 08:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_alter_property_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaseDocumentPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('OVERDUE', 'Overdue')], default='PENDING', max_length=10)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('landlord', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lease_document_payments', to=settings.AUTH_USER_MODEL)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lease_document_payments', to='api.property')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['property', 'landlord'], name='api_leasedo_propert_7fde51_idx'), models.Index(fields=['status'], name='api_leasedo_status_6f076f_idx')],
            },
        ),
    ]
