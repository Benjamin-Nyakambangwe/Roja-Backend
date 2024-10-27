from rest_framework import serializers
from rest_framework import serializers
from .models import Property, PropertyImage, Application, Message, LeaseAgreement, Review, HouseType, HouseLocation, Comment
from accounts.serializers import CustomUserSerializer, TenantProfileSerializer
from django.contrib.auth import get_user_model
from django.db.models import Max

User = get_user_model()

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'order']

# class PropertySerializer(serializers.ModelSerializer):
#     # owner = CustomUserSerializer(read_only=True)
#     images = PropertyImageSerializer(many=True, read_only=True)
#     main_image = PropertyImageSerializer(read_only=True)

#     class Meta:
#         model = Property
#         fields = ['id', 'owner', 'title', 'description', 'address', 'price', 'bedrooms', 'bathrooms', 'area', 'is_available', 'accepts_pets', 'pet_deposit', 'accepts_smokers', 'preferred_lease_term', 'main_image', 'images']

class CommentSerializer(serializers.ModelSerializer):
    # tenant = TenantProfileSerializer(read_only=True)
    # property = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'property', 'commenter', 'is_owner', 'content', 'created_at', 'updated_at']
        read_only_fields = ['commenter','created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['commenter'] = instance.commenter.first_name + " " + instance.commenter.last_name
        return representation


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    main_image = PropertyImageSerializer(read_only=True)
    image_files = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'owner', 'title', 'description', 'address', 'price', 'deposit', 'bedrooms', 'bathrooms', 'area', 'is_available', 'accepts_pets', 'pet_deposit', 'accepts_smokers', 'preferred_lease_term', 'pool', 'garden', 'type', 'location', 'main_image', 'images', 'image_files', 'comments', 'tenants_with_access', 'current_tenant']
        depth = 1

    def create(self, validated_data):
        image_files = validated_data.pop('image_files')
        property = Property.objects.create(**validated_data)

        for index, image_file in enumerate(image_files):
            PropertyImage.objects.create(property=property, image=image_file, order=index)

        if image_files:
            property.main_image = PropertyImage.objects.filter(property=property).first()
            property.save()
        return property

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
    sender = serializers.EmailField(source='sender.email', read_only=True)
    receiver = serializers.EmailField(source='receiver.email')

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read']
        read_only_fields = ['sender', 'timestamp', 'is_read']

    def create(self, validated_data):
        receiver_email = validated_data.pop('receiver')
        receiver = User.objects.get(email=receiver_email)
        return Message.objects.create(receiver=receiver, **validated_data)



class ChatSerializer(serializers.Serializer):
    chat_id = serializers.CharField()
    other_user = serializers.SerializerMethodField()
    last_message = MessageSerializer()
    unread_count = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    messages = MessageSerializer(many=True)

    def get_other_user(self, obj):
        return {
            'id': obj['other_user'].id,
            'email': obj['other_user'].email,
            'first_name': obj['other_user'].first_name,
            'last_name': obj['other_user'].last_name
        }


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




