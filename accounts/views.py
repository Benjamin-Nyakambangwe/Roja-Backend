from django.core.mail import send_mail
from django.db import transaction
from api.models import Property
from .serializers import TenantProfileLimitedSerializer
from .models import TenantProfile
from rest_framework import permissions, status
import time
import logging
import uuid
from rest_framework.permissions import AllowAny
import hashlib
from .models import Payment
from paynow import Paynow
from django.conf import settings
from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView)
from .serializers import CustomTokenObtainPairSerializer
from .serializers import TenantRatingSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status as drf_status
from .models import LandlordProfile, TenantProfile, PricingTier, TenantRating
from .serializers import LandlordProfileSerializer, TenantProfileSerializer
from api.models import RentPayment
from django.utils import timezone
from django.template.loader import render_to_string
from io import BytesIO
import os
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, EmailMessage
from api.models import Property, RentPayment, LeaseAgreement
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from bs4 import BeautifulSoup
from django.db.models import Avg
from decimal import Decimal
from accounts.models import LandlordBalance, WithdrawalRequest


class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            response.set_cookie(
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=drf_status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.AUTH_COOKIE)
        response.delete_cookie('refresh')
        return response


class LandlordProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = LandlordProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.user_type != 'landlord':
            return None
        return LandlordProfile.objects.get_or_create(user=self.request.user)[0]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=drf_status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=drf_status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=drf_status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=drf_status.HTTP_204_NO_CONTENT)


class TenantProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = TenantProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.user_type != 'tenant':
            return None
        return TenantProfile.objects.get_or_create(user=self.request.user)[0]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=drf_status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=drf_status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=drf_status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=drf_status.HTTP_204_NO_CONTENT)


# class LandlordListView(generics.ListAPIView):
#     queryset = User.objects.filter(user_type='landlord')
#     serializer_class = CustomUserSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def get_queryset(self):
#         return super().get_queryset().select_related('landlord_profile')

# class TenantListView(generics.ListAPIView):
#     queryset = User.objects.filter(user_type='tenant')
#     serializer_class = CustomUserSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def get_queryset(self):
#         return super().get_queryset().select_related('tenant_profile')

class LandlordProfileListView(generics.ListAPIView):
    queryset = LandlordProfile.objects.all()
    serializer_class = LandlordProfileSerializer
    permission_classes = [permissions.IsAdminUser]


class TenantProfileListView(generics.ListAPIView):
    queryset = TenantProfile.objects.all()
    serializer_class = TenantProfileSerializer
    permission_classes = [permissions.IsAdminUser]


class getTenantProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        tenant_profile = TenantProfile.objects.get(user__id=pk)
        serializer = TenantProfileSerializer(tenant_profile)
        return Response(serializer.data)


logger = logging.getLogger(__name__)


class InitiatePaymentView(APIView):
    # permission_classes = [AllowAny]

    def post(self, request):
        tenant_profile = TenantProfile.objects.get(user=request.user)
        email = request.data.get('email')
        phone = request.data.get('phone')
        # amount = request.data.get('amount')
        plan = request.data.get('plan')
        if plan == 'basic':
            amount = 0.005
            pricing_tier = PricingTier.objects.get(name='Basic')
        elif plan == 'standard':
            amount = 0.015
            pricing_tier = PricingTier.objects.get(name='Standard')
        elif plan == 'premium':
            amount = 0.030

            pricing_tier = PricingTier.objects.get(name='Premium')
        elif plan == 'luxury':
            amount = 0.050
            pricing_tier = PricingTier.objects.get(name='Luxury')
        else:

            return Response({'error': 'Invalid plan'}, status=drf_status.HTTP_400_BAD_REQUEST)

        paynow = Paynow(
            settings.PAYNOW_INTEGRATION_ID,
            settings.PAYNOW_INTEGRATION_KEY,
            settings.PAYNOW_RESULT_URL,
            settings.PAYNOW_RETURN_URL
        )

        reference = f'Order_{uuid.uuid4()}'
        payment = paynow.create_payment(reference, email)
        payment.add('Order Payment', float(amount))

        try:
            response = paynow.send_mobile(payment, phone, 'ecocash')

            if response.success:
                time.sleep(30)
                print('success')
                status = paynow.check_transaction_status(response.poll_url)
                print(status.status)
                if status.status == 'paid':
                    Payment.objects.create(
                        reference=reference,
                        poll_url=response.poll_url,
                        amount=amount,
                        phone=phone,
                        email=email,
                        status=status.status,
                        tenant=tenant_profile
                    )
                    # Update tenant profile
                    tenant_profile.subscription_plan = plan
                    tenant_profile.subscription_status = 'active'
                    tenant_profile.pricing_tier = pricing_tier
                    tenant_profile.num_properties = pricing_tier.max_properties
                    tenant_profile.save()

                    return Response({
                        'poll_url': response.poll_url,
                        'reference': reference,
                        'status': status.status
                    }, status=drf_status.HTTP_200_OK)
                else:
                    return Response({'error': 'Payment not successful'}, status=drf_status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': response.data['error']}, status=drf_status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentResultView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request):

        data = request.data
        hash_string = '&'.join(
            [f'{key}={data[key]}' for key in sorted(data.keys()) if key != 'hash'])
        local_hash = hashlib.sha512(
            (hash_string + settings.PAYNOW_INTEGRATION_KEY).encode('utf-8')).hexdigest()

        if local_hash != data.get('hash'):
            return Response({'error': 'Invalid hash'}, status=drf_status.HTTP_400_BAD_REQUEST)
        status_data = request.data
        reference = status_data.get('reference')
        payment = Payment.objects.filter(reference=reference).first()

        if payment:
            payment.status = status_data.get('status')
            payment.save()
            return Response({'status': 'Updated'}, status=drf_status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment not found'}, status=drf_status.HTTP_404_NOT_FOUND)


class PaymentStatusView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request):
        poll_url = request.data.get('poll_url')
        if not poll_url:
            return Response({'error': 'Poll URL is required'}, status=drf_status.HTTP_400_BAD_REQUEST)

        paynow = Paynow(
            settings.PAYNOW_INTEGRATION_ID,
            settings.PAYNOW_INTEGRATION_KEY,
        )

        response = paynow.poll_transaction(poll_url)

        if response.success:
            payment_status = response.status
            # Update your payment model if needed
            Payment.objects.filter(poll_url=poll_url).update(
                status=payment_status)
            return Response({'status': payment_status}, status=drf_status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to get payment status'}, status=drf_status.HTTP_400_BAD_REQUEST)


class TenantProfileLimitedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'tenant':
            return Response({"error": "Only tenants can access this information."}, status=drf_status.HTTP_403_FORBIDDEN)

        try:
            tenant_profile = TenantProfile.objects.get(user=request.user)
            serializer = TenantProfileLimitedSerializer(tenant_profile)
            return Response(serializer.data)
        except TenantProfile.DoesNotExist:
            return Response({"error": "Tenant profile not found."}, status=drf_status.HTTP_404_NOT_FOUND)


class LandlordProfileLimitedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        if request.user.user_type != 'tenant':
            return Response({"error": "Only tenants can access this information."}, status=drf_status.HTTP_403_FORBIDDEN)

        try:
            landlord_profile = LandlordProfile.objects.get(id=pk)
            serializer = LandlordProfileSerializer(landlord_profile)
            return Response(serializer.data)
        except LandlordProfile.DoesNotExist:
            return Response({"error": "Landlord profile not found."}, status=drf_status.HTTP_404_NOT_FOUND)


class AddTenantAccessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def send_email_notification(self, subject, context):
        html_message = render_to_string('email/tenant_access.html', context)

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[context['recipient_email']]
        )
        email.content_subtype = "html"  # Main content is now HTML
        email.send()

    @transaction.atomic
    def post(self, request, property_id):
        if request.user.user_type != 'tenant':
            return Response({"error": "Only tenants can access properties."}, status=status.HTTP_403_FORBIDDEN)

        try:
            property = Property.objects.get(id=property_id)
            tenant_profile = TenantProfile.objects.get(user=request.user)

            if tenant_profile.num_properties <= 0:
                return Response({"error": "You have reached the maximum number of properties you can access."}, status=status.HTTP_400_BAD_REQUEST)

            if request.user in property.tenants_with_access.all():
                return Response({"error": "You already have access to this property."}, status=status.HTTP_400_BAD_REQUEST)

            property.tenants_with_access.add(request.user)
            tenant_profile.num_properties -= 1
            tenant_profile.save()

            # Send email to landlord
            landlord_context = {
                'email_title': 'New Tenant Access Request',
                'property': property,
                'message': f"A new tenant, {request.user.first_name} {request.user.last_name}, has requested access to your property.",
                'tenant_profile_url': f"https://ro-ja.com/tenant-profile/{request.user.id}",
                'recipient_email': property.owner.email
            }
            self.send_email_notification(
                f"New Tenant Access Request for Property: {property.title}",
                landlord_context
            )

            # Send confirmation to tenant
            tenant_context = {
                'email_title': 'Property Access Confirmed',
                'property': property,
                'message': f"You now have access to view this property. The landlord will be notified of your interest.",
                'recipient_email': request.user.email
            }
            self.send_email_notification(
                f"Access Granted to Property: {property.title}",
                tenant_context
            )

            return Response({
                "message": "Access granted to the property and number of accessible properties updated. Notifications sent."
            }, status=status.HTTP_200_OK)

        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)
        except TenantProfile.DoesNotExist:
            return Response({"error": "Tenant profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({
                "error": "An error occurred while processing your request."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


logger = logging.getLogger(__name__)

# class SetCurrentTenantView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, property_id):
#         if request.user.user_type != 'landlord':
#             return Response({"error": "Only landlords can set current tenants."}, status=status.HTTP_403_FORBIDDEN)

#         property = get_object_or_404(Property, id=property_id, owner=request.user)
#         tenant_id = request.data.get('tenant_id')

#         if not tenant_id:
#             return Response({"error": "Tenant ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             tenant_profile = TenantProfile.objects.get(user__id=tenant_id)
#         except TenantProfile.DoesNotExist:
#             return Response({"error": "Tenant profile not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Store previous tenants with access
#         previous_tenants = list(property.tenants_with_access.all())

#         # Add current tenant to previous tenants
#         property.previous_tenants.add(property.current_tenant)

#         # Set current tenant
#         property.current_tenant = tenant_profile.user

#         # Clear tenants with access except for the winning tenant
#         property.tenants_with_access.clear()
#         property.tenants_with_access.add(tenant_profile.user)
#         property.previous_tenants_with_access.add(previous_tenants)

#         property.save()

#         # Send email to the winning tenant
#         self.send_email_to_winning_tenant(tenant_profile.user, property)

#         # Send email to the landlord
#         self.send_email_to_landlord(request.user, tenant_profile.user, property)

#         # Send emails to other tenants who had access
#         self.send_emails_to_other_tenants(previous_tenants, tenant_profile.user, property)

#         return Response({
#             "message": f"Current tenant set for property {property.title}. Notifications sent.",
#             "property_id": property.id,
#             "tenant_id": tenant_profile.id,
#             "tenant_name": f"{tenant_profile.user.first_name} {tenant_profile.user.last_name}"
#         }, status=status.HTTP_200_OK)

#     def send_email_to_winning_tenant(self, tenant, property):
#         subject = f"Congratulations! You've been selected for {property.title}"
#         message = f"Dear {tenant.first_name},\n\nCongratulations! You have been selected as the tenant for the property: {property.title}.\n\nBest regards,\nROJA ACCOMODATION Team"
#         self.send_email(subject, message, [tenant.email])

#     def send_email_to_landlord(self, landlord, tenant, property):
#         subject = f"Tenant Selected for {property.title}"
#         message = f"Dear {landlord.first_name},\n\nThis is to confirm that you have selected {tenant.first_name} {tenant.last_name} as the tenant for your property: {property.title}.\n\nBest regards,\nROJA ACCOMODATION Team"
#         self.send_email(subject, message, [landlord.email])

#     def send_emails_to_other_tenants(self, previous_tenants, winning_tenant, property):
#         for tenant in previous_tenants:
#             if tenant != winning_tenant:
#                 subject = f"Update on {property.title}"
#                 message = f"Dear {tenant.first_name},\n\nWe regret to inform you that you were not selected for the property: {property.title}. We appreciate your interest and encourage you to explore other available properties.\n\nBest regards,\nROJA ACCOMODATION Team"
#                 self.send_email(subject, message, [tenant.email])

#     def send_email(self, subject, message, recipient_list):
#         try:
#             send_mail(
#                 subject,
#                 message,
#                 settings.EMAIL_HOST_USER,
#                 recipient_list,
#                 fail_silently=False,
#             )
#         except Exception as e:
#             logger.error(f"Failed to send email. Error: {str(e)}")
#             print(f"Failed to send email. Error: {str(e)}")


class SetCurrentTenantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, property_id):
        if request.user.user_type != 'landlord':
            return Response({"error": "Only landlords can set current tenants."}, status=drf_status.HTTP_403_FORBIDDEN)

        property = get_object_or_404(
            Property, id=property_id, owner=request.user)
        tenant_id = request.data.get('tenant_id')

        if not tenant_id:
            return Response({"error": "Tenant ID is required."}, status=drf_status.HTTP_400_BAD_REQUEST)

        try:
            tenant_profile = TenantProfile.objects.get(user__id=tenant_id)
            tenant_user = tenant_profile.user
        except TenantProfile.DoesNotExist:
            return Response({"error": "Tenant profile not found."}, status=drf_status.HTTP_404_NOT_FOUND)

        # Store previous tenants with access
        previous_tenants = list(property.tenants_with_access.all())

        # Set current tenant
        property.current_tenant = tenant_user

        # Clear tenants with access except for the winning tenant
        property.tenants_with_access.clear()
        property.previous_tenants_with_access.add(*previous_tenants)
        property.tenants_with_access.add(tenant_user)

        # Create first rent payment if in-app payments are accepted
        if property.accepts_in_app_payment:
            next_month = timezone.now().date() + timezone.timedelta(days=30)
            RentPayment.objects.create(
                property=property,
                tenant=tenant_user,
                amount=property.price,
                due_date=next_month,
                status='PENDING'
            )

        property.save()

        # Send notifications...
        self.send_email_to_winning_tenant(tenant_user, property)
        self.send_email_to_landlord(request.user, tenant_user, property)
        self.send_emails_to_other_tenants(
            previous_tenants, tenant_user, property)

        return Response({
            "message": f"Current tenant set for property {property.title}. Notifications sent.",
            "property_id": property.id,
            "tenant_id": tenant_profile.user.id,
            "tenant_name": f"{tenant_profile.user.first_name} {tenant_profile.user.last_name}",
            "rent_payment_created": property.accepts_in_app_payment
        })

    def send_email_to_winning_tenant(self, tenant, property):
        subject = f"Congratulations! You've been selected for {property.title}"
        message = f"Dear {tenant.first_name},\n\nCongratulations! You have been selected as the tenant for the property: {property.title}.\n\nBest regards,\nROJA ACCOMODATION Team"
        self.send_email(subject, message, [tenant.email])

    def send_email_to_landlord(self, landlord, tenant, property):
        subject = f"Tenant Selected for {property.title}"
        message = f"Dear {landlord.first_name},\n\nThis is to confirm that you have selected {tenant.first_name} {tenant.last_name} as the tenant for your property: {property.title}.\n\nBest regards,\nROJA ACCOMODATION Team"
        self.send_email(subject, message, [landlord.email])

    def send_emails_to_other_tenants(self, previous_tenants, winning_tenant, property):
        for tenant in previous_tenants:
            if tenant != winning_tenant:
                subject = f"Update on {property.title}"
                message = f"Dear {tenant.first_name},\n\nWe regret to inform you that you were not selected for the property: {property.title}. We appreciate your interest and encourage you to explore other available properties.\n\nBest regards,\nROJA ACCOMODATION Team"
                self.send_email(subject, message, [tenant.email])

    def send_email(self, subject, message, recipient_list):
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send email. Error: {str(e)}")
            print(f"Failed to send email. Error: {str(e)}")


class RevokeCurrentTenantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, property_id):
        if request.user.user_type != 'landlord':
            return Response({"error": "Only landlords can revoke current tenants."}, status=drf_status.HTTP_403_FORBIDDEN)

        property = get_object_or_404(
            Property, id=property_id, owner=request.user)
        tenant_id = request.data.get('tenant_id')

        if not tenant_id:
            return Response({"error": "Tenant ID is required."}, status=drf_status.HTTP_400_BAD_REQUEST)

        try:
            tenant_profile = TenantProfile.objects.get(user__id=tenant_id)
            tenant_user = tenant_profile.user
        except TenantProfile.DoesNotExist:
            return Response({"error": "Tenant profile not found."}, status=drf_status.HTTP_404_NOT_FOUND)

        property.current_tenant = None
        # property.tenants_with_access.remove(tenant_user)  # Change this line
        property.previous_tenants.add(tenant_user)
        property.save()

        return Response({"message": f"Current tenant revoked for property {property.title}."}, status=drf_status.HTTP_200_OK)


class SetCurrentTenantWithLeaseDocView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def generate_lease_agreement(self, property, tenant, landlord, start_date):
        """Generate lease agreement PDF using template"""
        # Calculate end date (30 days from start)
        end_date = start_date + timezone.timedelta(days=30)

        # Prepare context for template
        context = {
            'generated_date': datetime.now().strftime('%d %B, %Y'),
            'landlord': landlord,
            'tenant': tenant,
            'property': property,
            'start_date': start_date.strftime('%d %B, %Y'),
            'end_date': end_date.strftime('%d %B, %Y'),
            'rent_amount': property.price,
            'deposit_amount': property.deposit,
            'payment_method': 'in-app payment' if property.accepts_in_app_payment else 'cash payment'
        }

        # Render HTML template
        html_string = render_to_string('lease_agreement.html', context)

        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Get styles
        styles = getSampleStyleSheet()
        elements = []

        # Clean and process HTML content
        soup = BeautifulSoup(html_string, 'html.parser')
        text_content = soup.get_text(separator='\n', strip=True)

        # Process each paragraph
        for paragraph in text_content.split('\n'):
            if paragraph.strip():
                try:
                    p = Paragraph(paragraph.strip(), styles['Normal'])
                    elements.append(p)
                    elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Error processing paragraph: {str(e)}")
                    continue

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def post(self, request, property_id):
        print("Received request data:", request.data)
        print("Property ID:", property_id)
        print("User type:", request.user.user_type)
        print("User:", request.user.email)

        if request.user.user_type != 'landlord':
            return Response({"error": "Only landlords can set current tenants."},
                            status=drf_status.HTTP_403_FORBIDDEN)

        try:
            property = get_object_or_404(
                Property, id=property_id, owner=request.user)
            print("Found property:", property.title)
        except:
            return Response({"error": "Property not found or not owned by user"},
                            status=drf_status.HTTP_404_NOT_FOUND)

        tenant_id = request.data.get('tenant_id')
        print("Tenant ID:", tenant_id)

        if not tenant_id:
            return Response({"error": "Tenant ID is required."},
                            status=drf_status.HTTP_400_BAD_REQUEST)

        try:
            tenant_profile = TenantProfile.objects.get(user__id=tenant_id)
            tenant_user = tenant_profile.user
            print("Found tenant:", tenant_user.email)
            print("Next of kin email:", tenant_profile.next_of_kin_email)

            # Store if tenant has next of kin email
            has_next_of_kin = tenant_profile.next_of_kin_email is not None

        except TenantProfile.DoesNotExist:
            return Response({"error": "Tenant profile not found."},
                            status=drf_status.HTTP_404_NOT_FOUND)

        # Store previous tenants
        previous_tenants = list(property.tenants_with_access.all())

        # Set dates
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=30)

        # Generate lease agreement
        lease_pdf = self.generate_lease_agreement(
            property=property,
            tenant=tenant_user,
            landlord=request.user,
            start_date=start_date
        )

        # Create lease agreement record
        lease_agreement = LeaseAgreement.objects.create(
            tenant=tenant_user,
            property=property,
            start_date=start_date,
            end_date=end_date,
            rent_amount=property.price
        )

        # Update property tenants
        property.current_tenant = tenant_user
        property.tenants_with_access.clear()
        property.previous_tenants_with_access.add(*previous_tenants)
        property.tenants_with_access.add(tenant_user)

        # Create rent payment if applicable
        if property.accepts_in_app_payment:
            RentPayment.objects.create(
                property=property,
                tenant=tenant_user,
                amount=property.price,
                due_date=end_date,
                status='PENDING'
            )

        property.save()

        # Send notifications with lease agreement
        self.send_email_to_winning_tenant(tenant_user, property, lease_pdf)
        self.send_email_to_landlord(
            request.user, tenant_user, property, lease_pdf)
        if has_next_of_kin:  # Only send to next of kin if email exists
            self.send_email_to_tenant_kin(
                tenant_profile.next_of_kin_email, tenant_user, property, lease_pdf)
        self.send_emails_to_other_tenants(
            previous_tenants, tenant_user, property)

        return Response({
            "message": f"Current tenant set for property {property.title}. Lease agreement sent to all parties.",
            "property_id": property.id,
            "tenant_id": tenant_user.id,
            "tenant_name": f"{tenant_user.first_name} {tenant_user.last_name}",
            "lease_start_date": start_date,
            "lease_end_date": end_date,
            "rent_payment_created": property.accepts_in_app_payment
        })

    def send_email_to_winning_tenant(self, tenant, property, lease_pdf):
        subject = f"Congratulations! You've been selected for {property.title}"
        message = f"""Dear {tenant.first_name},

Congratulations! You have been selected as the tenant for the property: {property.title}.

Please find attached the lease agreement for your review and records.

Best regards,
ROJA ACCOMODATION Team"""
        self.send_email_with_attachment(
            subject, message, [tenant.email], lease_pdf, "lease_agreement.pdf")

    def send_email_to_landlord(self, landlord, tenant, property, lease_pdf):
        subject = f"Tenant Selected for {property.title}"
        message = f"""Dear {landlord.first_name},

This is to confirm that you have selected {tenant.first_name} {tenant.last_name} as the tenant for your property: {property.title}.

Please find attached the lease agreement for your records.

Best regards,
ROJA ACCOMODATION Team"""
        self.send_email_with_attachment(
            subject, message, [landlord.email], lease_pdf, "lease_agreement.pdf")

    def send_email_to_tenant_kin(self, kin_email, tenant, property, lease_pdf):
        subject = f"Lease Agreement Witness - {property.title}"
        message = f"""Dear Sir/Madam,

You have been listed as a witness for the lease agreement between {tenant.first_name} {tenant.last_name} and ROJA ACCOMODATION for the property: {property.title}.

Please find attached the lease agreement for your review and records.

Best regards,
ROJA ACCOMODATION Team"""
        self.send_email_with_attachment(
            subject, message, [kin_email], lease_pdf, "lease_agreement.pdf")

    def send_emails_to_other_tenants(self, previous_tenants, winning_tenant, property):
        for tenant in previous_tenants:
            if tenant != winning_tenant:
                subject = f"Update on {property.title}"
                message = f"""Dear {tenant.first_name},

We regret to inform you that you were not selected for the property: {property.title}. We appreciate your interest and encourage you to explore other available properties.

Best regards,
ROJA ACCOMODATION Team"""
                self.send_email(subject, message, [tenant.email])

    def send_email(self, subject, message, recipient_list):
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email. Error: {str(e)}")

    def send_email_with_attachment(self, subject, message, recipient_list, pdf_file, filename):
        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.EMAIL_HOST_USER,
                to=recipient_list
            )
            email.attach(filename, pdf_file.getvalue(), 'application/pdf')
            email.send(fail_silently=False)
        except Exception as e:
            print(f"Failed to send email with attachment. Error: {str(e)}")


class TenantRatingCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            tenant_id = request.data.get('tenant')
            rating = request.data.get('rating')
            comment = request.data.get('comment')

            # Get tenant and landlord profiles
            tenant_profile = TenantProfile.objects.get(id=tenant_id)
            landlord_profile = request.user.landlord_profile

            # Create new rating
            rating_obj = TenantRating.objects.create(
                tenant=tenant_profile,
                landlord=landlord_profile,
                rating=rating,
                comment=comment
            )

            # Update tenant's overall rating (average of all ratings)
            avg_rating = TenantRating.objects.filter(
                tenant=tenant_profile
            ).aggregate(Avg('rating'))['rating__avg']

            tenant_profile.current_rating = round(float(avg_rating), 2)
            tenant_profile.save()

            serializer = TenantRatingSerializer(rating_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TenantRatingListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, tenant_id=None):
        try:
            if tenant_id:
                # Get ratings for specific tenant
                ratings = TenantRating.objects.filter(tenant_id=tenant_id)
            else:
                # Get all ratings made by the landlord
                try:
                    landlord_profile = request.user.landlord_profile
                    ratings = TenantRating.objects.filter(
                        landlord=landlord_profile)
                except:
                    return Response({
                        'error': 'Only landlords can view ratings'
                    }, status=status.HTTP_403_FORBIDDEN)

            serializer = TenantRatingSerializer(ratings, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LandlordBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'landlord':
            return Response({
                'error': 'Only landlords can access balance information'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get or create balance
        balance, created = LandlordBalance.objects.get_or_create(
            landlord=request.user)

        # Get recent transactions (rent payments for landlord properties)
        properties = Property.objects.filter(owner=request.user)
        transactions = RentPayment.objects.filter(
            property__in=properties,
            status='PAID'
        ).order_by('-payment_date')[:10]

        # Get pending withdrawal requests
        withdrawal_requests = WithdrawalRequest.objects.filter(
            landlord=request.user
        ).order_by('-requested_at')[:5]

        # Serialize the data
        transaction_data = [{
            'id': t.id,
            'property': t.property.title,
            'tenant': f"{t.tenant.first_name} {t.tenant.last_name}",
            'amount': t.amount,
            'payment_date': t.payment_date,
            'transaction_id': t.transaction_id
        } for t in transactions]

        withdrawal_data = [{
            'id': w.id,
            'amount': w.amount,
            'status': w.status,
            'reference': w.reference,
            'requested_at': w.requested_at,
            'processed_at': w.processed_at
        } for w in withdrawal_requests]

        return Response({
            'balance': balance.amount,
            'last_updated': balance.last_updated,
            'recent_transactions': transaction_data,
            'withdrawal_requests': withdrawal_data
        })


class CreateWithdrawalRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'landlord':
            return Response({
                'error': 'Only landlords can request withdrawals'
            }, status=status.HTTP_403_FORBIDDEN)

        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        bank_name = request.data.get('bank_name')
        account_number = request.data.get('account_number')
        account_name = request.data.get('account_name')
        notes = request.data.get('notes')

        if not amount:
            return Response({
                'error': 'Amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
        except:
            return Response({
                'error': 'Amount must be a valid number'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if landlord has sufficient balance
        balance, created = LandlordBalance.objects.get_or_create(
            landlord=request.user)

        if balance.amount < amount:
            return Response({
                'error': 'Insufficient balance for withdrawal',
                'current_balance': balance.amount,
                'requested_amount': amount
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create withdrawal request
        withdrawal = WithdrawalRequest.objects.create(
            landlord=request.user,
            amount=amount,
            payment_method=payment_method,
            bank_name=bank_name,
            account_number=account_number,
            account_name=account_name,
            notes=notes
        )

        # Reduce balance immediately to prevent double withdrawals
        balance.amount -= amount
        balance.save()

        # Send notification to admin
        self.notify_admin(withdrawal)

        return Response({
            'success': True,
            'message': 'Withdrawal request submitted successfully',
            'reference': withdrawal.reference,
            'amount': withdrawal.amount,
            'new_balance': balance.amount
        })

    def notify_admin(self, withdrawal):
        """Send notification to admin about new withdrawal request"""
        try:
            subject = f"New Withdrawal Request: {withdrawal.reference}"
            message = f"""
            A new withdrawal request has been submitted:
            
            Reference: {withdrawal.reference}
            Landlord: {withdrawal.landlord.email} ({withdrawal.landlord.first_name} {withdrawal.landlord.last_name})
            Amount: ${withdrawal.amount}
            Payment Method: {withdrawal.payment_method or 'Not specified'}
            Bank: {withdrawal.bank_name or 'Not specified'}
            Account: {withdrawal.account_number or 'Not specified'} ({withdrawal.account_name or 'Not specified'})
            Notes: {withdrawal.notes or 'None'}
            
            Please process this request through the admin interface.
            """

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [settings.SUPPORT_EMAIL],
                fail_silently=False
            )
        except Exception as e:
            print(f"Failed to send admin notification: {str(e)}")
