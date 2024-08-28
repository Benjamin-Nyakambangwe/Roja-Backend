from rest_framework import serializers
from rest_framework import serializers
from .models import Property, PropertyImage, Application, Message, LeaseAgreement, Review, HouseType, HouseLocation
from accounts.serializers import CustomUserSerializer


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'order']

class PropertySerializer(serializers.ModelSerializer):
    # owner = CustomUserSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    main_image = PropertyImageSerializer(read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'owner', 'title', 'description', 'address', 'price', 'bedrooms', 'bathrooms', 'area', 'is_available', 'accepts_pets', 'pet_deposit', 'accepts_smokers', 'preferred_lease_term', 'main_image', 'images']

class HouseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseType
        fields = ['id', 'name']

class HouseLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseLocation
        fields = ['id', 'name', 'city']



class ApplicationSerializer(serializers.ModelSerializer):
    applicant = CustomUserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'applicant', 'property', 'status', 'application_date']

class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)
    receiver = CustomUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read']

class LeaseAgreementSerializer(serializers.ModelSerializer):
    tenant = CustomUserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = LeaseAgreement
        fields = ['id', 'tenant', 'property', 'start_date', 'end_date', 'rent_amount', 'is_signed']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = CustomUserSerializer(read_only=True)
    reviewed = CustomUserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewed', 'property', 'rating', 'comment', 'created_at']




# from .models import Site, LinkRequest, LinkRequestStatus, Niche


# class NicheSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Niche
#         fields = ['id', 'name']

# class SiteSerializer(serializers.ModelSerializer):
#     niche = NicheSerializer(read_only=True)
#     niche_id = serializers.PrimaryKeyRelatedField(queryset=Niche.objects.all(), source='niche', write_only=True)

#     class Meta:
#         model = Site
#         fields = '__all__'

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation['publisher'] = instance.publisher.phone  # Assuming publisher has a name field
#         # representation['publisher'] = instance.publisher.name  # Assuming publisher has a name field
#         return representation



# class LinkRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LinkRequest
#         fields = '__all__'

# class LinkRequestStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LinkRequestStatus
#         fields = '__all__'

