from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import LandlordProfile, TenantProfile, PricingTier, TenantRating
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'user_type')

class LandlordProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandlordProfile
        fields = '__all__'
        read_only_fields = ('user', 'is_profile_complete', 'is_verified', 'last_updated')
        depth = 1

class PricingTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingTier
        fields = ['name']

class TenantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantProfile
        fields = '__all__'
        read_only_fields = ('user', 'is_profile_complete', 'last_updated')
        depth = 1

class CustomUserSerializer(UserCreateSerializer):
    landlord_profile = LandlordProfileSerializer(required=False)
    tenant_profile = TenantProfileSerializer(required=False)

    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'user_type', 'landlord_profile', 'tenant_profile')

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        landlord_profile = validated_data.pop('landlord_profile', None)
        tenant_profile = validated_data.pop('tenant_profile', None)

        user = User.objects.create_user(**validated_data, user_type=user_type)

        if user_type == 'landlord' and landlord_profile:
            LandlordProfile.objects.create(user=user, **landlord_profile)
        elif user_type == 'tenant' and tenant_profile:
            TenantProfile.objects.create(user=user, **tenant_profile)

        return user
    


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_type'] = user.user_type  # Assuming user_type is a field in your User model
        # You can add other custom claims here

        return token

class TenantProfileLimitedSerializer(serializers.ModelSerializer):
    pricing_tier = PricingTierSerializer(read_only=True)

    class Meta:
        model = TenantProfile
        fields = ['num_properties', 'subscription_plan', 'subscription_status', 'pricing_tier']



class TenantRatingSerializer(serializers.ModelSerializer):
    tenant_name = serializers.SerializerMethodField()
    landlord_name = serializers.SerializerMethodField()

    class Meta:
        model = TenantRating
        fields = ['id', 'tenant', 'landlord', 'rating', 'comment', 'created_at', 
                 'tenant_name', 'landlord_name']
        read_only_fields = ['landlord', 'created_at']

    def get_tenant_name(self, obj):
        return f"{obj.tenant.user.first_name} {obj.tenant.user.last_name}"

    def get_landlord_name(self, obj):
        return f"{obj.landlord.user.first_name} {obj.landlord.user.last_name}"