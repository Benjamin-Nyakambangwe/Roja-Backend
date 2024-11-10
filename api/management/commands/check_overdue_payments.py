from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import RentPayment

class Command(BaseCommand):
    help = 'Check for overdue rent payments'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        overdue_payments = RentPayment.objects.filter(
            status='PENDING',
            due_date__lt=today
        )
        
        for payment in overdue_payments:
            payment.status = 'OVERDUE'
            payment.save()
            
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {overdue_payments.count()} overdue payments'
            )
        ) 