from django.conf import settings
from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import(TokenObtainPairView, TokenRefreshView, TokenVerifyView)
from .serializers import CustomTokenObtainPairSerializer

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status as drf_status
from .models import LandlordProfile, TenantProfile, PricingTier
from .serializers import LandlordProfileSerializer, TenantProfileSerializer
from api.models import RentPayment
from django.utils import timezone

class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKE_PATH, 
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
                )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKE_PATH, 
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
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKE_PATH, 
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
                )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKE_PATH, 
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
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKE_PATH, 
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
        serializer = self.get_serializer(instance, data=request.data, partial=True)
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
        serializer = self.get_serializer(instance, data=request.data, partial=True)
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


    
            
        
from paynow import Paynow
from django.conf import settings
from .models import Payment
import hashlib
from rest_framework.permissions import AllowAny
import uuid
import logging
import time
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
            amount = 5
            pricing_tier = PricingTier.objects.get(name='Basic')
        elif plan == 'standard':
            amount = 15
            pricing_tier = PricingTier.objects.get(name='Standard')
        elif plan == 'premium':
            amount = 30
            pricing_tier = PricingTier.objects.get(name='Premium')
        elif plan == 'luxury':
            amount = 50
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
                Payment.objects.create(
                    reference=reference,
                    poll_url=response.poll_url,
                    amount=amount,
                    phone=phone,
                    email=email,
                    status = status.status,
                    tenant = tenant_profile
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
                return Response({'error': response.data['error']}, status=drf_status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)



class PaymentResultView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication
    def post(self, request):

        data = request.data
        hash_string = '&'.join([f'{key}={data[key]}' for key in sorted(data.keys()) if key != 'hash'])
        local_hash = hashlib.sha512((hash_string + settings.PAYNOW_INTEGRATION_KEY).encode('utf-8')).hexdigest()

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
            Payment.objects.filter(poll_url=poll_url).update(status=payment_status)
            return Response({'status': payment_status}, status=drf_status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to get payment status'}, status=drf_status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import TenantProfile
from .serializers import TenantProfileLimitedSerializer
from django.shortcuts import get_object_or_404

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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from api.models import Property
from .models import TenantProfile
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

class AddTenantAccessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, property_id):
        if request.user.user_type != 'tenant':
            return Response({"error": "Only tenants can access properties."}, status=drf_status.HTTP_403_FORBIDDEN)
        
        try:
            property = Property.objects.get(id=property_id)
            tenant_profile = TenantProfile.objects.get(user=request.user)

            if tenant_profile.num_properties <= 0:
                return Response({"error": "You have reached the maximum number of properties you can access."}, status=status.HTTP_400_BAD_REQUEST)

            if request.user in property.tenants_with_access.all():
                return Response({"error": "You already have access to this property."}, status=drf_status.HTTP_400_BAD_REQUEST)

            property.tenants_with_access.add(request.user)
            tenant_profile.num_properties -= 1
            tenant_profile.save()

            # Send email to landlord with tenant profile link
            landlord_email = property.owner.email
            tenant_name = f"{request.user.first_name} {request.user.last_name}"
            property_title = property.title
            tenant_profile_url = f"https://beta.ro-ja.com/tenant-profile/{request.user.id}"

            subject = f"New Tenant Access Request for Property: {property_title}"
            message = f"""Dear Landlord,

A new tenant, {tenant_name}, has requested access to your property: {property_title}.

To view the tenant's full profile and credentials, click here:
{tenant_profile_url}

You can review their profile and make an informed decision about their application.

Best regards,
ROJA ACCOMODATION Team"""

            from_email = settings.EMAIL_HOST_USER
            recipient_list = [landlord_email]

            print(f"Attempting to send email to: {landlord_email}")
            print(f"Attempting to send email from: {settings.EMAIL_HOST_USER}")
            try:
                send_mail(subject, message, from_email, recipient_list)
                print("Email sent successfully")
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                # You might want to add this error to the response
                return Response({
                    "message": "Access granted to the property and number of accessible properties updated.",
                    "warning": f"Failed to notify landlord via email. Error: {str(e)}"
                }, status=status.HTTP_200_OK)

            return Response({
                "message": "Access granted to the property and number of accessible properties updated. Landlord has been notified."
            }, status=status.HTTP_200_OK)

        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=drf_status.HTTP_404_NOT_FOUND)
        except TenantProfile.DoesNotExist:
            return Response({"error": "Tenant profile not found."}, status=drf_status.HTTP_404_NOT_FOUND)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from api.models import Property
from .models import TenantProfile
from django.shortcuts import get_object_or_404
import logging

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
        
        property = get_object_or_404(Property, id=property_id, owner=request.user)
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
        self.send_emails_to_other_tenants(previous_tenants, tenant_user, property)
        
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
        
        property = get_object_or_404(Property, id=property_id, owner=request.user)
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

