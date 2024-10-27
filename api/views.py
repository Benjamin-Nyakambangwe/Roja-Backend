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

from .models import Property, PropertyImage, Application, Message, LeaseAgreement, Review, HouseType, HouseLocation, Comment
from .serializers import PropertySerializer, PropertyImageSerializer, ApplicationSerializer, MessageSerializer, LeaseAgreementSerializer, ReviewSerializer, HouseTypeSerializer, HouseLocationSerializer, CommentSerializer, ChatSerializer
from accounts.models import TenantProfile
from collections import defaultdict  # Add this import


# Property views
class PropertyList(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class OwnPropertyList(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]  # Changed to IsAuthenticated

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
        # Return properties where current_tenant is null by default
        return Property.objects.filter(current_tenant__isnull=True)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request, format=None):
        queryset = self.get_queryset()
        
        # Check if a query parameter is provided to show all properties
        show_all = request.query_params.get('show_all', 'false').lower() == 'true'
        
        if show_all:
            queryset = Property.objects.all()
        
        filtered_queryset = self.filter_queryset(queryset)
        serializer = PropertySerializer(filtered_queryset, many=True)
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

#House Location Views
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
from django.contrib.auth import get_user_model

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
        unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
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

# Explanation:
# This class, CommentList, is a view that handles listing all comments and creating new ones.
# It uses Django Rest Framework's ListCreateAPIView, which provides GET (list) and POST (create) functionality.

# Key points:
# 1. queryset: Retrieves all Comment objects from the database.
# 2. serializer_class: Uses CommentSerializer to convert Comment objects to/from JSON.
# 3. permission_classes: Allows authenticated users to create comments, but anyone can read them.
# 4. perform_create method: Overrides the default behavior when creating a comment.
#    It gets the TenantProfile associated with the current user and sets it as the tenant for the new comment.
#    This ensures that comments are always associated with the correct tenant profile.

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

from django.db.models import Q, Max, Count, Case, When, IntegerField, F
from django.contrib.auth import get_user_model
from .serializers import ChatSerializer, MessageSerializer

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
            unread_count=Count(Case(When(receiver=user, is_read=False, then=1)))
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
        queryset.filter(receiver=request.user, is_read=False).update(is_read=True)
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
            unread_count=Count(Case(When(receiver=user, is_read=False, then=1))),
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

            chat_dict[other_user_id]['messages'].update(messages)  # Use update instead of extend

        # Convert sets back to sorted lists
        for chat in chat_dict.values():
            chat['messages'] = sorted(chat['messages'], key=lambda x: x.timestamp)

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
