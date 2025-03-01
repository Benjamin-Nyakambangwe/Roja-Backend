from django.db.models import Q, Max, Count, Case, When, IntegerField, F, Avg
from .serializers import ChatSerializer, MessageSerializer
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
# from .models import Site
# from .serializers import SiteSerializer
# from .filters import SiteFilter
from rest_framework.permissions import AllowAny
from .filters import PropertyFilter
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Property, PropertyImage, Application, Message, LeaseAgreement, Review, HouseType, HouseLocation, Comment, RentPayment, PhoneVerification, LeaseDocumentPayment
from .serializers import PropertySerializer, PropertyImageSerializer, ApplicationSerializer, MessageSerializer, LeaseAgreementSerializer, ReviewSerializer, HouseTypeSerializer, HouseLocationSerializer, CommentSerializer, ChatSerializer, RentPaymentSerializer, LeaseDocumentPaymentSerializer
from accounts.models import TenantProfile
from collections import defaultdict  # Add this import

from accounts.serializers import CustomUserSerializer

from django.utils import timezone

import uuid
import time

from paynow import Paynow

from .utils import add_watermark

import openai

from twilio.rest import Client

import random

from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

# from infobip_api_client.api_client import ApiClient, Configuration
# from infobip_api_client.model.sms_advanced_textual_request import SmsAdvancedTextualRequest
# from infobip_api_client.model.sms_destination import SmsDestination
# from infobip_api_client.model.sms_textual_message import SmsTextualMessage
# from infobip_api_client.api.send_sms_api import SendSmsApi

import http.client
import json


# Property views
class PropertyList(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Get image files directly from request.FILES
        image_files = self.request.FILES.getlist('image_files')

        if not image_files:
            raise serializers.ValidationError(
                {"image_files": "At least one image is required"})

        # Create property instance with owner
        property_instance = serializer.save(owner=self.request.user)

        # Process each image
        for index, image_file in enumerate(image_files):
            # Add watermark to image
            watermarked_image = add_watermark(image_file)

            # Create PropertyImage instance with watermarked image
            PropertyImage.objects.create(
                property=property_instance,
                image=watermarked_image,
                order=index
            )

        # Set main image
        property_instance.main_image = PropertyImage.objects.filter(
            property=property_instance
        ).first()
        property_instance.save()

        # Send approval email
        try:
            # Get the domain
            domain = 'https://api.ro-ja.com'

            # Update URLs to match the actual endpoints
            approve_url = f"{domain}/api/properties/{property_instance.id}/approve/"
            disapprove_url = f"{domain}/api/properties/{property_instance.id}/disapprove/"

            # Get owner's profile
            owner_profile = self.request.user.landlord_profile

            # Prepare email attachments with proper MIME types
            attachments = []
            if property_instance.affidavit:
                file_name = property_instance.affidavit.name.split(
                    '/')[-1]  # Get original filename
                content_type = self._get_content_type(file_name)
                attachments.append((
                    file_name,
                    property_instance.affidavit.read(),
                    content_type
                ))

            if property_instance.proof_of_residence:
                file_name = property_instance.proof_of_residence.name.split(
                    '/')[-1]
                content_type = self._get_content_type(file_name)
                attachments.append((
                    file_name,
                    property_instance.proof_of_residence.read(),
                    content_type
                ))

            # Prepare email context
            context = {
                'property': property_instance,
                'approve_url': approve_url,
                'disapprove_url': disapprove_url,
                'site_name': 'ROJA ACCOMODATION',
                'domain': domain,
                'owner': self.request.user,
                'owner_profile': owner_profile,
            }

            # Render email template
            html_message = render_to_string(
                'email/property_approval.html', context)

            # Create email message
            email = EmailMessage(
                subject=f'New Property Approval Required: {property_instance.title}',
                body=html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.SUPPORT_EMAIL],
            )
            email.content_subtype = "html"

            # Add attachments
            for attachment in attachments:
                email.attach(*attachment)

            # Send email
            email.send(fail_silently=False)
            print(
                f"Property approval email sent successfully for: {property_instance.title}")

        except Exception as e:
            print(f"Failed to send property approval email: {str(e)}")
            # Don't raise error, just log it
            # Property creation was successful even if email fails

    def _get_content_type(self, filename):
        """Helper method to determine content type based on file extension"""
        extension = filename.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        return content_types.get(extension, 'application/octet-stream')


class OwnPropertyList(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    # Changed to IsAuthenticated
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the properties
        for the currently authenticated user.
        """
        return Property.objects.filter(owner=self.request.user)


class PropertyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PropertyListCreateView(APIView):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['price', 'bedrooms', 'bathrooms', 'area']
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Property.objects.filter(current_tenant__isnull=True, is_approved=True).order_by('-overall_rating')

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request, format=None):
        queryset = self.get_queryset()

        show_all = request.query_params.get(
            'show_all', 'false').lower() == 'true'

        if show_all:
            queryset = Property.objects.all().order_by('-id')

        filtered_queryset = self.filter_queryset(queryset)
        serializer = PropertySerializer(
            filtered_queryset, many=True, context={'request': request})
        return Response(serializer.data)


# PropertyImage views
class PropertyImageList(generics.ListCreateAPIView):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PropertyImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# House Type Views
class HouseTypeList(generics.ListCreateAPIView):
    queryset = HouseType.objects.all()
    serializer_class = HouseTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class HouseTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = HouseType.objects.all()
    serializer_class = HouseTypeSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# House Location Views


class HouseLocationList(generics.ListCreateAPIView):
    queryset = HouseLocation.objects.all()
    serializer_class = HouseLocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class HouseLocationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = HouseLocation.objects.all()
    serializer_class = HouseLocationSerializer

# Application views


class ApplicationList(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class ApplicationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]


# Message views

User = get_user_model()


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(receiver=user))

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        receiver_email = request.data.get('receiver')
        if not receiver_email:
            return Response({"error": "Receiver email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            return Response({"error": f"User with email {receiver_email} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=self.request.user, receiver=receiver)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)


class UnreadMessageCountView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        unread_count = Message.objects.filter(
            receiver=request.user, is_read=False).count()
        return Response({"unread_count": unread_count})


class MarkMessageAsReadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            message = Message.objects.get(id=pk, receiver=request.user)
            message.is_read = True
            message.save()
            return Response({"status": "Message marked as read"}, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)

# Review views


class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        property_id = self.request.data.get('property')
        reviewed_id = self.request.data.get('reviewed')

        if not property_id:
            raise serializers.ValidationError("Property ID is required")
        if not reviewed_id:
            raise serializers.ValidationError("Reviewed user ID is required")

        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            raise serializers.ValidationError("Invalid Property ID")

        try:
            reviewed_user = get_user_model().objects.get(id=reviewed_id)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("Invalid Reviewed User ID")

        serializer.save(
            reviewer=self.request.user,
            property=property_instance,
            reviewed=reviewed_user
        )

    def create(self, request, *args, **kwargs):
        print("User:", request.user)
        print("Auth:", request.auth)
        print("Headers:", request.headers)
        return super().create(request, *args, **kwargs)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Comment views


class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(commenter=self.request.user)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(commenter=self.request.user)


class PropertyCommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        property_id = self.kwargs['property_id']
        return Comment.objects.filter(property_id=property_id)

    def perform_create(self, serializer):
        property_id = self.kwargs['property_id']
        property = Property.objects.get(id=property_id)
        serializer.save(commenter=self.request.user, property=property)


User = get_user_model()


class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        chats = Message.objects.filter(Q(sender=user) | Q(receiver=user)).values(
            'sender', 'receiver'
        ).annotate(
            last_message_id=Max('id'),
            other_user_id=Case(
                When(sender=user, then=F('receiver')),
                default=F('sender'),
                output_field=IntegerField(),
            ),
            unread_count=Count(
                Case(When(receiver=user, is_read=False, then=1)))
        ).order_by('-last_message_id')

        return [
            {
                'other_user': User.objects.get(id=chat['other_user_id']),
                'last_message': Message.objects.get(id=chat['last_message_id']),
                'unread_count': chat['unread_count']
            }
            for chat in chats
        ]


class ChatDetailView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.kwargs['user_id']
        return Message.objects.filter(
            (Q(sender=user) & Q(receiver_id=other_user_id)) |
            (Q(receiver=user) & Q(sender_id=other_user_id))
        ).order_by('timestamp')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.filter(receiver=request.user,
                        is_read=False).update(is_read=True)
        return super().list(request, *args, **kwargs)


class AvailableChatsView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        chats = Message.objects.filter(Q(sender=user) | Q(receiver=user)).values(
            'sender', 'receiver'
        ).annotate(
            last_message_id=Max('id'),
            other_user_id=Case(
                When(sender=user, then=F('receiver')),
                default=F('sender'),
                output_field=IntegerField(),
            ),
            unread_count=Count(
                Case(When(receiver=user, is_read=False, then=1))),
            total_messages=Count('id', distinct=True)  # Use distinct=True here
        ).order_by('-last_message_id')

        chat_dict = {}

        for chat in chats:
            other_user_id = chat['other_user_id']
            if other_user_id not in chat_dict:
                other_user = User.objects.get(id=other_user_id)
                chat_dict[other_user_id] = {
                    'chat_id': f"{min(user.id, other_user_id)}_{max(user.id, other_user_id)}",
                    'other_user': other_user,
                    'last_message': Message.objects.get(id=chat['last_message_id']),
                    'unread_count': chat['unread_count'],
                    'total_messages': chat['total_messages'],
                    'messages': set()  # Use a set instead of a list to avoid duplicates
                }

            messages = Message.objects.filter(
                (Q(sender=user) & Q(receiver_id=other_user_id)) |
                (Q(receiver=user) & Q(sender_id=other_user_id))
            ).order_by('timestamp')

            chat_dict[other_user_id]['messages'].update(
                messages)  # Use update instead of extend

        # Convert sets back to sorted lists
        for chat in chat_dict.values():
            chat['messages'] = sorted(
                chat['messages'], key=lambda x: x.timestamp)

        return list(chat_dict.values())

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PropertyReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        property_id = self.kwargs['property_id']
        return Review.objects.filter(property_id=property_id)


class UserReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Review.objects.filter(reviewed_id=user_id)

# class SetCurrentTenantView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, property_id):
#         if request.user.user_type != 'landlord':
#             return Response({"error": "Only landlords can set current tenants."}, status=status.HTTP_403_FORBIDDEN)

#         from django.shortcuts import get_object_or_404
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

#         # Add current tenant to previous tenants if it exists
#         # if property.current_tenant is not None:
#         #     property.previous_tenants.add(property.current_tenant)

#         # Set current tenant
#         property.current_tenant = tenant_profile.user

#         # Clear tenants with access except for the winning tenant
#         property.tenants_with_access.clear()
#         property.tenants_with_access.add(tenant_profile.user)

#         # Add previous tenants to previous_tenants_with_access
#         # for tenant in previous_tenants:
#         #     if tenant != tenant_profile.user:
#         #         property.previous_tenants_with_access.add(tenant)

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
#             "tenant_id": tenant_profile.user.id,
#             "tenant_name": f"{tenant_profile.user.first_name} {tenant_profile.user.last_name}"
#         }, status=status.HTTP_200_OK)

#     # ... (keep the email sending methods as they were)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


class CommentLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            print(
                f"Attempting to like comment {pk} by user {request.user.email}")
            comment = Comment.objects.get(pk=pk)
            print(f"Found comment: {comment}")
            print(f"Current likes: {comment.get_like_count()}")
            liked = comment.toggle_like(request.user)
            print(
                f"After toggle - liked: {liked}, new count: {comment.get_like_count()}")
            return Response({
                'liked': liked,
                'like_count': comment.get_like_count(),
                'dislike_count': comment.get_dislike_count(),
                'has_liked': comment.has_user_liked(request.user),
                'has_disliked': comment.has_user_disliked(request.user)
            })
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error in like view: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommentDislikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            disliked = comment.toggle_dislike(request.user)
            return Response({
                'disliked': disliked,
                'like_count': comment.get_like_count(),
                'dislike_count': comment.get_dislike_count()
            })
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class RentPaymentListView(generics.ListCreateAPIView):
    serializer_class = RentPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'landlord':
            return RentPayment.objects.filter(property__owner=self.request.user)
        return RentPayment.objects.filter(tenant=self.request.user)

    def perform_create(self, serializer):
        property_id = self.request.data.get('property')
        property_instance = Property.objects.get(id=property_id)

        if property_instance.current_tenant != self.request.user:
            raise serializers.ValidationError(
                "Only current tenant can create rent payments")

        serializer.save(
            tenant=self.request.user,
            property=property_instance,
            amount=property_instance.price
        )


class PropertyRentPaymentsView(generics.ListAPIView):
    serializer_class = RentPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        property_id = self.kwargs['property_id']
        property = Property.objects.get(id=property_id)

        if not (self.request.user == property.owner or
                self.request.user == property.current_tenant):
            return RentPayment.objects.none()

        return RentPayment.objects.filter(property_id=property_id)


class ProcessRentPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, payment_id):
        try:
            payment = RentPayment.objects.get(
                id=payment_id, tenant=request.user)
            if payment.status != 'PENDING':
                return Response(
                    {"error": "Payment is not in pending status"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get payment details from request
            email = request.data.get('email')
            phone = request.data.get('phone')

            if not email or not phone:
                return Response({
                    'error': 'Email and phone number are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Initialize Paynow
            paynow = Paynow(
                settings.PAYNOW_INTEGRATION_ID,
                settings.PAYNOW_INTEGRATION_KEY,
                settings.PAYNOW_RESULT_URL,
                settings.PAYNOW_RETURN_URL
            )

            # Create payment reference
            reference = f'Rent_{payment.id}_{uuid.uuid4()}'
            paynow_payment = paynow.create_payment(reference, email)
            paynow_payment.add('Rent Payment', float(0.02))
            # TODO: change to payment.amount

            try:
                response = paynow.send_mobile(paynow_payment, phone, 'ecocash')

                if response.success:
                    time.sleep(30)  # Wait for payment processing
                    status_response = paynow.check_transaction_status(
                        response.poll_url)

                    if status_response.status == 'paid':
                        # Update rent payment
                        payment.status = 'PAID'
                        payment.payment_date = timezone.now().date()
                        payment.transaction_id = reference
                        payment.save()

                        # Update landlord balance
                        payment.update_landlord_balance()

                        # Create next month's payment
                        next_due_date = payment.due_date + \
                            timezone.timedelta(days=30)
                        RentPayment.objects.create(
                            property=payment.property,
                            tenant=payment.tenant,
                            amount=payment.amount,
                            due_date=next_due_date,
                            status='PENDING'
                        )

                        return Response({
                            "message": "Payment processed successfully and next month's payment created",
                            # "payment": RentPaymentSerializer(payment).data,
                            "poll_url": response.poll_url,
                            "reference": reference,
                            "status": status_response.status
                        })
                    else:
                        return Response({
                            "error": "Payment not completed",
                            "status": status_response.status
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        'error': response.data['error']
                    }, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except RentPayment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class TenantAccessibleProperties(generics.ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return properties where:
        1. The user is in tenants_with_access OR
        2. The user is the current_tenant OR
        # 3. The user is in previous_tenants_with_access
        """
        user = self.request.user

        if user.user_type != 'tenant':
            return Property.objects.none()

        return Property.objects.filter(
            Q(tenants_with_access=user) |
            Q(current_tenant=user)
            # Q(previous_tenants_with_access=user)
        ).distinct()


class TenantCurrentProperty(generics.ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return the current property of the tenant
        """
        user = self.request.user

        if user.user_type != 'tenant':
            return Property.objects.none()

        return Property.objects.filter(
            current_tenant=user
        ).distinct()


class GeneratePropertyDescriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Get property details from form data
            title = request.data.get('title', '')
            bedrooms = request.data.get('bedrooms', '')
            bathrooms = request.data.get('bathrooms', '')
            area = request.data.get('area', '')
            property_type = request.data.get('type', '')
            location = request.data.get('location', '')

            # Log incoming data
            print(f"Received data: {request.data}")

            # Convert string 'on' to boolean for checkboxes
            accepts_pets = request.data.get('accepts_pets') == 'on'
            pool = request.data.get('pool') == 'on'
            garden = request.data.get('garden') == 'on'

            features = []
            if accepts_pets:
                features.append('Pet-friendly')
            if pool:
                features.append('Swimming pool')
            if garden:
                features.append('Garden')

            # Get HouseType and HouseLocation names if IDs are provided
            try:
                if property_type:
                    house_type = HouseType.objects.get(id=property_type)
                    property_type = house_type.name
                if location:
                    house_location = HouseLocation.objects.get(id=location)
                    location = f"{house_location.name}, {house_location.city}" if house_location.city else house_location.name
            except HouseType.DoesNotExist:
                print(f"HouseType with ID {property_type} not found")
                return Response({"error": f"House type with ID {property_type} not found"}, status=status.HTTP_404_NOT_FOUND)
            except HouseLocation.DoesNotExist:
                print(f"HouseLocation with ID {location} not found")
                return Response({"error": f"Location with ID {location} not found"}, status=status.HTTP_404_NOT_FOUND)

            # Log processed data
            print(
                f"Processed data - Type: {property_type}, Location: {location}, Features: {features}")

            # Check if OpenAI API key is configured
            if not settings.OPENAI_API_KEY:
                print("OpenAI API key not configured")
                return Response(
                    {"error": "OpenAI API key not configured"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Construct the prompt
            prompt = f"""Please provide a detailed property description to attract potential tenants by highlighting key aspects using the given description below:

Property Details:
- Title: {title}
- Type: {property_type}
- Location: {location}
- Bedrooms: {bedrooms}
- Bathrooms: {bathrooms}
- Area: {area} square feet
- Features: {', '.join(features)}

Start by describing the property type and include specifics like the number of bedrooms, bathrooms, and area. Next, emphasize unique features that set this property apart. Finally, include details about any additional amenities."""

            print("Making OpenAI API call...")
            try:
                # Configure OpenAI client
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

                # Make API call using new format
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system",
                            "content": "You are a professional real estate copywriter."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )

                # Extract the generated description
                description = response.choices[0].message.content.strip()
                print("Successfully generated description")

                return Response({
                    'description': description
                })

            except openai.APIError as e:
                print(f"OpenAI API Error: {str(e)}")
                return Response(
                    {"error": f"OpenAI API Error: {str(e)}"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            except openai.RateLimitError as e:
                print(f"Rate limit exceeded: {str(e)}")
                return Response(
                    {"error": "Rate limit exceeded. Please try again later."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            except openai.AuthenticationError as e:
                print(f"Authentication error: {str(e)}")
                return Response(
                    {"error": "Invalid API key"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {
                    "error": "An unexpected error occurred",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendSMSView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            phone_number = request.data.get('phone_number')
            message = request.data.get('message')

            if not phone_number or not message:
                return Response({
                    'error': 'Phone number and message are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Initialize Twilio client
            client = Client(settings.TWILIO_ACCOUNT_SID,
                            settings.TWILIO_AUTH_TOKEN)

            # Send message
            message = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )

            return Response({
                'success': True,
                'message_sid': message.sid
            })

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendVerificationCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def generate_code(self):
        return ''.join(random.choices('0123456789', k=6))

    def post(self, request):
        try:
            # Get phone number based on user type
            if request.user.user_type == 'landlord':
                try:
                    profile = request.user.landlord_profile
                except:
                    return Response({
                        'error': 'Landlord profile not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    profile = request.user.tenant_profile
                except:
                    return Response({
                        'error': 'Tenant profile not found'
                    }, status=status.HTTP_404_NOT_FOUND)

            if not profile.phone:
                return Response({
                    'error': 'No phone number found in profile'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Generate verification code
            verification_code = self.generate_code()

            # Save verification code
            PhoneVerification.objects.create(
                user=request.user,
                verification_code=verification_code
            )

            # Create connection
            conn = http.client.HTTPSConnection(settings.INFOBIP_BASE_URL)

            # Prepare payload
            payload = json.dumps({
                "messages": [
                    {
                        "destinations": [{"to": profile.phone}],
                        "from": "RO-JA",
                        "text": f"Your ROJA ACCOMODATION verification code is: {verification_code}. This code will expire in 5 minutes."
                    }
                ]
            })

            # Prepare headers
            headers = {
                'Authorization': f'App {settings.INFOBIP_API_KEY}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # Send request
            conn.request("POST", "/sms/2/text/advanced", payload, headers)

            # Get response
            res = conn.getresponse()
            data = res.read()

            # Close connection
            conn.close()

            if res.status in [200, 201]:
                return Response({
                    'success': True,
                    'message': 'Verification code sent successfully'
                })
            else:
                return Response({
                    'error': f'Failed to send SMS: {data.decode("utf-8")}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"Error sending verification code: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPhoneCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            verification_code = request.data.get('code')

            if not verification_code:
                return Response({
                    'error': 'Verification code is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get latest verification code for this user
            verification = PhoneVerification.objects.filter(
                user=request.user,
                is_verified=False
            ).order_by('-created_at').first()

            if not verification:
                return Response({
                    'error': 'No pending verification found'
                }, status=status.HTTP_404_NOT_FOUND)

            if verification.is_expired():
                return Response({
                    'error': 'Verification code has expired'
                }, status=status.HTTP_400_BAD_REQUEST)

            if verification.verification_code != verification_code:
                return Response({
                    'error': 'Invalid verification code'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Mark as verified
            verification.is_verified = True
            verification.save()

            # Update user's profile
            if request.user.user_type == 'landlord':
                profile = request.user.landlord_profile
            else:
                profile = request.user.tenant_profile

            profile.is_phone_verified = True
            profile.save()

            print(profile.is_phone_verified)

            return Response({
                'success': True,
                'message': 'Phone number verified successfully'
            })

        except Exception as e:
            print(f"Error verifying code: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentReplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        try:
            # Get the parent comment
            parent_comment = Comment.objects.get(id=comment_id)

            # Don't allow replies to replies
            if parent_comment.is_reply:
                return Response(
                    {"error": "Cannot reply to a reply"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get content from request
            content = request.data.get('content')
            if not content:
                return Response(
                    {"error": "Content is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the reply
            reply = Comment.objects.create(
                property=parent_comment.property,
                commenter=request.user,
                content=content,
                parent=parent_comment,
                is_reply=True,
                is_owner=parent_comment.property.owner == request.user
            )

            # Serialize and return the reply
            serializer = CommentSerializer(reply, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ApprovePropertyView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow any user to access

    def post(self, request, property_id):
        try:
            # Get property
            property = Property.objects.get(id=property_id)

            # Update property status
            property.is_approved = True
            property.save()

            # Send notification to property owner
            subject = f'Your Property Has Been Approved: {property.title}'
            message = f"""Dear {property.owner.first_name},

Your property listing "{property.title}" has been approved and is now visible on our platform.

Best regards,
ROJA ACCOMODATION Team"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[property.owner.email],
                fail_silently=False,
            )

            return Response({
                "message": f"Property {property.title} has been approved",
                "property_id": property.id
            })

        except Property.DoesNotExist:
            return Response(
                {"error": "Property not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DisapprovePropertyView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow any user to access

    def post(self, request, property_id):
        try:
            # Get property
            property = Property.objects.get(id=property_id)

            # Get reason for disapproval
            reason = request.data.get('reason', 'No reason provided')

            # Update property status
            property.is_approved = False
            property.save()

            # Send notification to property owner
            subject = f'Your Property Was Not Approved: {property.title}'
            message = f"""Dear {property.owner.first_name},

Your property listing "{property.title}" was not approved for the following reason:

{reason}

Please make the necessary adjustments and submit again.

Best regards,
ROJA ACCOMODATION Team"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[property.owner.email],
                fail_silently=False,
            )

            return Response({
                "message": f"Property {property.title} has been disapproved",
                "property_id": property.id,
                "reason": reason
            })

        except Property.DoesNotExist:
            return Response(
                {"error": "Property not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContactFormView(APIView):
    # Allow anyone to contact support
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            # Get form data
            name = request.data.get('name')
            email = request.data.get('email')
            message = request.data.get('message')

            # Validate required fields
            if not all([name, email, message]):
                return Response({
                    'error': 'Name, email and message are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Prepare email content
            subject = f'New Contact Form Submission from {name}'
            html_message = render_to_string('email/contact_form.html', {
                'name': name,
                'email': email,
                'message': message,
                'submitted_at': timezone.now().strftime('%B %d, %Y, %I:%M %p'),
                'site_name': 'ROJA ACCOMODATION'
            })

            # Send email
            email_message = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.EMAIL_HOST_USER,
                to=['support@ro-ja.com', 'benjaminnyakambangwe@gmail.com'],
                # Allow support to reply directly to the sender
                reply_to=[email]
            )
            email_message.content_subtype = "html"  # Main content is now HTML
            email_message.send()

            return Response({
                'message': 'Your message has been sent successfully. We will get back to you soon.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error sending contact form: {str(e)}")
            return Response({
                'error': 'Failed to send message. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateLandlordRatingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def calculate_profile_completeness(self, profile):
        """Calculate profile completeness percentage and bonus rating"""
        fields_to_check = {
            # Most important verifications (highest weights)
            'is_phone_verified': 1.0,  # Phone verification is most important
            'is_verified': 0.8,        # General verification
            'is_profile_complete': 0.8,  # Profile completion status

            # Identity verification (high weights)
            'id_number': 0.7,
            'id_image': 0.7,
            'proof_of_residence': 0.7,

            # Contact information (medium-high weights)
            'phone': 0.6,
            'alternate_phone': 0.4,
            'emergency_contact_name': 0.5,
            'emergency_contact_phone': 0.5,

            # Personal information (medium weights)
            'profile_image': 0.5,
            'date_of_birth': 0.4,
            'marital_status': 0.3,

            # Additional information (lower weights)
            'additional_notes': 0.2
        }

        completeness_score = 0
        max_score = sum(fields_to_check.values())

        for field, weight in fields_to_check.items():
            field_value = getattr(profile, field, None)
            if field_value not in [None, '', False]:  # Check for empty values
                completeness_score += weight

        # Convert to percentage
        completeness_percentage = (completeness_score / max_score) * 100

        # Calculate bonus rating (up to 1.0 extra points for a fully complete profile)
        bonus_rating = (completeness_percentage / 100) * 1.0

        return completeness_percentage, bonus_rating

    def post(self, request):
        try:
            landlords = get_user_model().objects.filter(user_type='landlord')
            updated_count = 0
            ratings_details = []

            for landlord in landlords:
                try:
                    # Get all properties owned by this landlord
                    properties = Property.objects.filter(owner=landlord)
                    total_rating = 0
                    total_reviews = 0

                    # Calculate property reviews rating
                    for property in properties:
                        property_reviews = Review.objects.filter(
                            property=property)
                        if property_reviews.exists():
                            total_rating += sum(
                                review.rating for review in property_reviews)
                            total_reviews += property_reviews.count()

                    # Calculate base rating from reviews
                    base_rating = 0
                    if total_reviews > 0:
                        base_rating = total_rating / total_reviews

                    # Calculate profile completeness and bonus
                    landlord_profile = landlord.landlord_profile
                    completeness_percentage, profile_bonus = self.calculate_profile_completeness(
                        landlord_profile)

                    # Calculate final rating (base rating + profile completeness bonus)
                    final_rating = base_rating + profile_bonus
                    # Cap at 5.0 and round to 1 decimal
                    final_rating = min(5.0, round(final_rating, 1))

                    # Update profile
                    landlord_profile.current_rating = final_rating
                    landlord_profile.profile_completeness = round(
                        completeness_percentage, 1)
                    landlord_profile.save()
                    updated_count += 1

                    # Store details for response
                    ratings_details.append({
                        "landlord_name": f"{landlord.first_name} {landlord.last_name}",
                        "email": landlord.email,
                        "base_rating": round(base_rating, 1),
                        "profile_completeness": round(completeness_percentage, 1),
                        "profile_bonus": round(profile_bonus, 1),
                        "final_rating": final_rating,
                        "total_reviews": total_reviews
                    })

                except Exception as e:
                    print(
                        f"Error updating landlord {landlord.email}: {str(e)}")

            return Response({
                "message": f"Successfully updated {updated_count} landlord ratings",
                "total_landlords": landlords.count(),
                "ratings_details": ratings_details
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Get current ratings and profile completeness for all landlords"""
        try:
            landlords = get_user_model().objects.filter(user_type='landlord')
            ratings_data = []

            for landlord in landlords:
                try:
                    profile = landlord.landlord_profile
                    properties = Property.objects.filter(owner=landlord)
                    completeness_percentage, _ = self.calculate_profile_completeness(
                        profile)

                    ratings_data.append({
                        "landlord_name": f"{landlord.first_name} {landlord.last_name}",
                        "email": landlord.email,
                        "current_rating": profile.current_rating,
                        "profile_completeness": round(completeness_percentage, 1),
                        "total_properties": properties.count(),
                        "total_reviews": Review.objects.filter(property__in=properties).count()
                    })

                except Exception as e:
                    print(
                        f"Error getting data for landlord {landlord.email}: {str(e)}")

            return Response(ratings_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalyzeCommentSentimentsView(APIView):
    permission_classes = [permissions.AllowAny]

    def analyze_sentiment(self, comment_text):
        """Use OpenAI to analyze comment sentiment and return a rating"""
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            messages = [
                {"role": "system", "content": "You are a sentiment analysis expert. Rate the following property comment on a scale of 1 to 5, where 1 is very negative and 5 is very positive. Only respond with a single number."},
                {"role": "user", "content": comment_text}
            ]

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                max_tokens=10,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            # Extract the rating from the response
            rating = float(response.choices[0].message.content.strip())
            return min(max(rating, 1), 5)  # Ensure rating is between 1 and 5

        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return None

    def post(self, request):
        try:
            # Get unrated comments
            unrated_comments = Comment.objects.filter(is_rated=False)

            if not unrated_comments.exists():
                return Response({
                    "message": "No unrated comments found"
                }, status=status.HTTP_200_OK)

            results = []
            for comment in unrated_comments:
                try:
                    # Get sentiment rating
                    sentiment_rating = self.analyze_sentiment(comment.content)

                    if sentiment_rating:
                        # Update comment with the AI-generated rating
                        comment.ai_rating = sentiment_rating
                        comment.is_rated = True
                        comment.save()

                        results.append({
                            "comment_id": comment.id,
                            "content": comment.content,
                            "ai_rating": sentiment_rating,
                            "property": comment.property.title,
                            "commenter": f"{comment.commenter.first_name} {comment.commenter.last_name}"
                        })

                except Exception as e:
                    print(f"Error processing comment {comment.id}: {str(e)}")
                    continue

            return Response({
                "message": f"Successfully analyzed {len(results)} comments",
                "results": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Get statistics about rated and unrated comments"""
        try:
            total_comments = Comment.objects.count()
            rated_comments = Comment.objects.filter(is_rated=True).count()
            unrated_comments = Comment.objects.filter(is_rated=False).count()

            # Get average AI ratings
            avg_rating = Comment.objects.filter(
                is_rated=True
            ).aggregate(Avg('ai_rating'))['ai_rating__avg']

            return Response({
                "total_comments": total_comments,
                "rated_comments": rated_comments,
                "unrated_comments": unrated_comments,
                "average_ai_rating": round(avg_rating, 2) if avg_rating else None
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdatePropertyRatingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def to_float(self, value):
        """Convert Decimal to float safely"""
        if value is None:
            return 0.0
        return float(value)

    def calculate_property_rating(self, property):
        """Calculate overall property rating based on reviews, comments, and landlord rating"""
        try:
            # Get all reviews for the property
            reviews = Review.objects.filter(property=property)
            review_count = reviews.count()
            avg_review_rating = 0.0

            if review_count > 0:
                review_ratings = sum(self.to_float(review.rating)
                                     for review in reviews)
                avg_review_rating = review_ratings / review_count

            # Get all AI-rated comments
            comments = Comment.objects.filter(
                property=property,
                is_rated=True,
                ai_rating__isnull=False
            )
            comment_count = comments.count()
            avg_comment_rating = 0.0

            if comment_count > 0:
                comment_ratings = sum(self.to_float(comment.ai_rating)
                                      for comment in comments)
                avg_comment_rating = comment_ratings / comment_count

            # Get landlord rating
            landlord_rating = 0.0
            try:
                landlord_profile = property.owner.landlord_profile
                if landlord_profile and landlord_profile.current_rating:
                    landlord_rating = self.to_float(
                        landlord_profile.current_rating)
            except Exception as e:
                print(f"Error getting landlord rating: {str(e)}")

            # Define base weights and adjust based on available data
            base_weights = {
                'review': 0.5,    # 50% for reviews
                'comment': 0.3,   # 30% for comments
                'landlord': 0.2   # 20% for landlord rating
            }

            # Determine which components are valid
            has_reviews = review_count > 0
            has_comments = comment_count > 0
            has_landlord_rating = landlord_rating > 0

            # Calculate adjusted weights based on available components
            adjusted_weights = {}
            total_base = 0

            if has_reviews:
                adjusted_weights['review'] = base_weights['review']
                total_base += base_weights['review']

            if has_comments:
                adjusted_weights['comment'] = base_weights['comment']
                total_base += base_weights['comment']

            if has_landlord_rating:
                # Only count landlord rating if there's at least one other component
                if has_reviews or has_comments:
                    adjusted_weights['landlord'] = base_weights['landlord']
                    total_base += base_weights['landlord']
                else:
                    # If only landlord rating exists, cap its weight
                    # Cap at 30% if it's the only component
                    adjusted_weights['landlord'] = 0.3
                    total_base = 0.3

            # Normalize weights if necessary
            if total_base > 0:
                for key in adjusted_weights:
                    adjusted_weights[key] = adjusted_weights[key] / total_base

            # Calculate weighted average
            weighted_sum = 0.0
            if has_reviews:
                weighted_sum += float(avg_review_rating) * \
                    adjusted_weights['review']
            if has_comments:
                weighted_sum += float(avg_comment_rating) * \
                    adjusted_weights['comment']
            if has_landlord_rating:
                weighted_sum += float(landlord_rating) * \
                    adjusted_weights['landlord']

            # Calculate final rating
            overall_rating = weighted_sum if total_base > 0 else 0.0

            return {
                'overall_rating': round(float(overall_rating), 1),
                'review_rating': round(float(avg_review_rating), 1),
                'comment_rating': round(float(avg_comment_rating), 1),
                'landlord_rating': round(float(landlord_rating), 1),
                'review_count': review_count,
                'comment_count': comment_count,
                'weights_used': adjusted_weights,
                'components_present': {
                    'has_reviews': has_reviews,
                    'has_comments': has_comments,
                    'has_landlord_rating': has_landlord_rating
                }
            }

        except Exception as e:
            print(
                f"Error calculating rating for property {property.id}: {str(e)}")
            return None

    def post(self, request):
        try:
            # Get all properties
            properties = Property.objects.all()
            updated_count = 0
            results = []

            for property in properties:
                try:
                    rating_data = self.calculate_property_rating(property)

                    if rating_data:
                        # Update property rating
                        property.overall_rating = rating_data['overall_rating']
                        property.save()
                        updated_count += 1

                        # Store results
                        results.append({
                            "property_id": property.id,
                            "title": property.title,
                            "overall_rating": rating_data['overall_rating'],
                            "review_rating": rating_data['review_rating'],
                            "comment_rating": rating_data['comment_rating'],
                            "review_count": rating_data['review_count'],
                            "comment_count": rating_data['comment_count']
                        })

                except Exception as e:
                    print(f"Error updating property {property.id}: {str(e)}")
                    continue

            return Response({
                "message": f"Successfully updated {updated_count} property ratings",
                "total_properties": properties.count(),
                "results": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Get current ratings for all properties"""
        try:
            properties = Property.objects.all()
            ratings_data = []

            for property in properties:
                try:
                    rating_data = self.calculate_property_rating(property)
                    if rating_data:
                        ratings_data.append({
                            "property_id": property.id,
                            "title": property.title,
                            "current_rating": property.overall_rating,
                            "calculated_rating": rating_data['overall_rating'],
                            "review_rating": rating_data['review_rating'],
                            "comment_rating": rating_data['comment_rating'],
                            "review_count": rating_data['review_count'],
                            "comment_count": rating_data['comment_count']
                        })

                except Exception as e:
                    print(
                        f"Error getting data for property {property.id}: {str(e)}")

            return Response(ratings_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessLeaseDocumentPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Get payment details from request first
            email = request.data.get('email')
            phone = request.data.get('phone')
            propertyId = request.data.get('property_id')
            amount = 0.02  # Fixed amount for lease document payment - specify as float

            print("Request data:", request.data)
            print("Property ID:", propertyId)
            print("Email:", email)
            print("Phone:", phone)

            if not all([email, phone, propertyId]):
                return Response({
                    'error': 'Email, phone number and propertyId required'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                property = Property.objects.get(id=propertyId)
            except Property.DoesNotExist:
                return Response({
                    'error': f'Property with ID {propertyId} not found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Create payment record without specifying ID
            payment = LeaseDocumentPayment.objects.create(
                landlord=request.user,
                amount=amount,
                status='PENDING',
                property=property
            )

            print("Payment created:", payment.id)

            # Initialize Paynow
            paynow = Paynow(
                settings.PAYNOW_INTEGRATION_ID,
                settings.PAYNOW_INTEGRATION_KEY,
                settings.PAYNOW_RESULT_URL,
                settings.PAYNOW_RETURN_URL
            )

            # Create payment reference
            reference = f'lease_document_{payment.id}_{uuid.uuid4()}'
            print("Payment reference:", reference)

            paynow_payment = paynow.create_payment(reference, email)
            print("TRACK 1")
            # Make sure amount is converted to float
            paynow_payment.add('Lease Document Payment', float(amount))
            print("TRACK 2")
            print("Attempting mobile payment...")
            response = paynow.send_mobile(paynow_payment, phone, 'ecocash')
            print("TRACK 3")
            print("Paynow response:", response.__dict__)

            if response.success:
                print("TRACK 4")
                time.sleep(30)  # Wait for payment processing
                status_response = paynow.check_transaction_status(
                    response.poll_url)
                print("TRACK 5")
                print("Status response:", status_response.__dict__)
                print(status_response.status)

                if status_response.status == 'paid':
                    print("TRACK 6")
                    payment.status = 'PAID'
                    print("TRACK 7")
                    payment.payment_date = timezone.now().date()
                    print("TRACK 8")
                    payment.transaction_id = reference
                    print("TRACK 9")
                    payment.save()
                    print("TRACK 10")
                    return Response({
                        "message": "Payment processed successfully",
                        # "payment": LeaseDocumentPaymentSerializer(payment).data,
                        "poll_url": response.poll_url,
                        "reference": reference,
                        "status": status_response.status
                    })
                    print("TRACK 11")
                else:
                    print("TRACK 12")
                    return Response({

                        "error": "Payment not completed",
                        "status": status_response.status
                    }, status=status.HTTP_400_BAD_REQUEST)
                    print("TRACK 13")
            else:
                print("TRACK 14")
                error_message = response.data.get('error') if hasattr(
                    response, 'data') else 'Payment initialization failed'
                print("TRACK 15")
                return Response({

                    'error': error_message
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("TRACK 20")
            print("General error:", str(e))
            return Response({

                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
