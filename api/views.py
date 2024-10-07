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
        return Property.objects.all()

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request, format=None):
        queryset = self.get_queryset()
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
        receiver_id = self.request.data.get('receiver')
        try:
            receiver = User.objects.get(id=receiver_id)
            serializer.save(sender=self.request.user, receiver=receiver)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid receiver ID")

    def create(self, request, *args, **kwargs):
        if 'receiver' not in request.data:
            return Response({"error": "Receiver is required"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

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
        tenant_profile = TenantProfile.objects.get(user=self.request.user)
        serializer.save(tenant=tenant_profile)

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
        tenant_profile = TenantProfile.objects.get(user=self.request.user)
        serializer.save(tenant=tenant_profile)

class PropertyCommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        property_id = self.kwargs['property_id']
        return Comment.objects.filter(property_id=property_id)

    def perform_create(self, serializer):
        property_id = self.kwargs['property_id']
        property = Property.objects.get(id=property_id)
        tenant_profile = TenantProfile.objects.get(user=self.request.user)
        serializer.save(tenant=tenant_profile, property=property)

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


