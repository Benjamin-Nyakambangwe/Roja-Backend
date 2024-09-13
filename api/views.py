from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
# from .models import Site
# from .serializers import SiteSerializer
# from .filters import SiteFilter
from rest_framework.permissions import AllowAny
from .filters import PropertyFilter





# class OwnSiteListView(APIView):
#     def get(self, request):
#         # Get the authenticated user
#         # Filter sites by the authenticated user
#         queryset = Site.objects.all()
#         serializer = SiteSerializer(queryset, many=True)
#         return Response(serializer.data)

# class SiteListCreateView(APIView):
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_class = SiteFilter
#     search_fields = ['name', 'domain', 'niche__name']
#     ordering_fields = ['domain_authority', 'organic_traffic', 'price_per_link', 'available_slots']
#     permission_classes = [AllowAny]

#     def filter_queryset(self, queryset):
#         for backend in list(self.filter_backends):
#             queryset = backend().filter_queryset(self.request, queryset, self)
#         return queryset

#     def get(self, request):
#         queryset = Site.objects.select_related('niche', 'publisher').all()
#         filtered_queryset = self.filter_queryset(queryset)
#         serializer = SiteSerializer(filtered_queryset, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = SiteSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class SiteRetrieveUpdateDestroyView(APIView):
#     def get_object(self, pk):
#         try:
#             return Site.objects.get(pk=pk)
#         except Site.DoesNotExist:
#             return None

#     def get(self, request, pk):
#         site = self.get_object(pk)
#         if site is not None:
#             serializer = SiteSerializer(site)
#             return Response(serializer.data)
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     def put(self, request, pk):
#         site = self.get_object(pk)
#         if site is not None:
#             serializer = SiteSerializer(site, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     def delete(self, request, pk):
#         site = self.get_object(pk)
#         if site is not None:
#             site.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_404_NOT_FOUND)
    


from rest_framework import generics, permissions
from .models import Property, PropertyImage, Application, Message, LeaseAgreement, Review, HouseType, HouseLocation, Comment
from .serializers import PropertySerializer, PropertyImageSerializer, ApplicationSerializer, MessageSerializer, LeaseAgreementSerializer, ReviewSerializer, HouseTypeSerializer, HouseLocationSerializer, CommentSerializer
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
class MessageList(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

# LeaseAgreement views
class LeaseAgreementList(generics.ListCreateAPIView):
    queryset = LeaseAgreement.objects.all()
    serializer_class = LeaseAgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)

class LeaseAgreementDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaseAgreement.objects.all()
    serializer_class = LeaseAgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

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