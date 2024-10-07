from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount, LandlordProfile, TenantProfile, PricingTier, Payment




class CustomUserAdmin(UserAdmin):
    model = UserAccount
    list_display = ('id','email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active',)
    list_filter = ('email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'password')}),
        ('Permissions', {'fields': ('user_type', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'user_type', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('email',)

admin.site.register(UserAccount, CustomUserAdmin)


@admin.register(PricingTier)
class PricingTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'max_properties', 'max_property_price', 'target')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(LandlordProfile)
class LandlordProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_profile_complete', 'is_verified', 'last_updated')
    list_filter = ('is_profile_complete', 'is_verified')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone', 'emergency_contact_name')
    fieldsets = (
        ('Personal Information', {'fields': ('user', 'date_of_birth', 'phone', 'alternate_phone', 'profile_image', 'id_image', 'id_number', 'proof_of_residence', 'marital_status')}),
        # ('Preferences', {'fields': ('preferred_lease_term', 'accepts_pets', 'pet_deposit', 'accepts_smokers')}),
        # ('Rental Policies', {'fields': ('screening_criteria', 'required_documents')}),
        # ('Maintenance', {'fields': ('handles_own_maintenance', 'preferred_contractors')}),
        ('Emergency Contact', {'fields': ('emergency_contact_name', 'emergency_contact_phone')}),
        ('Additional Information', {'fields': ('additional_notes',)}),
        ('Profile Status', {'fields': ('is_profile_complete', 'is_verified', 'last_updated')}),
    )
    readonly_fields = ('last_updated',)

@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'occupation', 'is_profile_complete', 'last_updated')
    list_filter = ('is_profile_complete', 'pets', 'smoker', 'has_vehicle', 'criminal_record')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone', 'occupation', 'employer')
    fieldsets = (
        ('Personal Information', {'fields': ('user', 'date_of_birth', 'gender', 'phone', 'emergency_contact_name', 'emergency_contact_phone', 'profile_image', 'id_image', 'id_number', 'proof_of_employment', 'marital_status')}),
        ('Employment', {'fields': ('occupation', 'employer', 'work_phone')}),
        ('Preferences', {'fields': ('preferred_lease_term', 'max_rent', 'preferred_move_in_date', 'preferred_area')}),
        ('Additional Information', {'fields': ('number_of_occupants', 'pets', 'pet_details', 'smoker', 'has_vehicle', 'num_of_vehicles')}),
        ('Financial Information', {'fields': ('criminal_record',)}),
        ('References', {'fields': ('personal_reference_1_name', 'personal_reference_1_phone', 'personal_reference_1_relation',
                                   'personal_reference_2_name', 'personal_reference_2_phone', 'personal_reference_2_relation')}),
        ('Additional Notes', {'fields': ('additional_notes',)}),
        ('Profile Status', {'fields': ('is_profile_complete', 'last_updated')}),
        ('Subscription', {'fields': ('subscription_plan', 'subscription_status', 'pricing_tier', 'num_properties')}),
    )
    readonly_fields = ('last_updated',)



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'amount', 'phone', 'email', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('reference', 'phone', 'email')
    ordering = ('-created_at',)


