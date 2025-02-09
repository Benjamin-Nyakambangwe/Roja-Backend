from rest_framework import serializers
from rest_framework import serializers
from .models import Property, PropertyImage, Application, Message, LeaseAgreement, Review, HouseType, HouseLocation, Comment, RentPayment, LeaseDocumentPayment
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
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    has_disliked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    commenter_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'property', 'commenter', 'commenter_name', 'is_owner', 
                 'content', 'created_at', 'updated_at', 'like_count', 
                 'dislike_count', 'has_liked', 'has_disliked', 'parent', 
                 'is_reply', 'replies']
        read_only_fields = ['commenter', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.is_reply:
            return []
        replies = Comment.objects.filter(parent=obj).order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_commenter_name(self, obj):
        return f"{obj.commenter.first_name} {obj.commenter.last_name}"

    def get_like_count(self, obj):
        return obj.get_like_count()

    def get_dislike_count(self, obj):
        return obj.get_dislike_count()

    def get_has_liked(self, obj):
        user = self.context['request'].user
        return obj.has_user_liked(user) if user.is_authenticated else False

    def get_has_disliked(self, obj):
        user = self.context['request'].user
        return obj.has_user_disliked(user) if user.is_authenticated else False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['commenter'] = instance.commenter.first_name + " " + instance.commenter.last_name
        return representation


class HouseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseType
        fields = ['id', 'name']

class HouseLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseLocation
        fields = ['id', 'name', 'city']


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    main_image = PropertyImageSerializer(read_only=True)
    image_files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        write_only=True,
        required=False
    )
    comments = CommentSerializer(many=True, read_only=True)
    type = serializers.PrimaryKeyRelatedField(queryset=HouseType.objects.all(), required=False, write_only=True)
    location = serializers.PrimaryKeyRelatedField(queryset=HouseLocation.objects.all(), required=False, write_only=True)
    type_detail = HouseTypeSerializer(source='type', read_only=True)
    location_detail = HouseLocationSerializer(source='location', read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'owner', 'title', 'description', 'address', 'price', 'deposit', 
                 'bedrooms', 'bathrooms', 'area', 'is_available', 'accepts_pets', 
                 'pet_deposit', 'accepts_smokers', 'preferred_lease_term', 'pool', 
                 'garden', 'type', 'location', 'type_detail', 'location_detail', 
                 'main_image', 'images', 'image_files', 'comments', 
                 'tenants_with_access', 'current_tenant', 'accepts_in_app_payment',
                 'accepts_cash_payment', 'proof_of_residence', 'affidavit', 'overall_rating']
        depth = 1

    def create(self, validated_data):
        # Remove image_files if present
        validated_data.pop('image_files', None)
        type_id = validated_data.pop('type', None)
        location_id = validated_data.pop('location', None)
        
        property = Property.objects.create(**validated_data)

        if type_id:
            property.type = type_id
        if location_id:
            property.location = location_id
        property.save()
            
        return property




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

class RentPaymentSerializer(serializers.ModelSerializer):
    tenant = CustomUserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = RentPayment
        fields = ['id', 'property', 'tenant', 'amount', 'due_date', 
                 'payment_date', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['transaction_id', 'created_at']



class LeaseDocumentPaymentSerializer(serializers.ModelSerializer):
    landlord = CustomUserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = LeaseDocumentPayment
        fields = ['id', 'property', 'landlord', 'amount', 'payment_date', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['transaction_id', 'created_at']



