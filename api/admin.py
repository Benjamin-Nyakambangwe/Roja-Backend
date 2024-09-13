from django.contrib import admin
from .models import Property, PropertyImage, Application, Message, LeaseAgreement, Review, HouseType, HouseLocation, Comment



class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'owner', 'price', 'bedrooms', 'bathrooms', 'accepts_pets', 'is_available')
    list_filter = ('is_available', 'bedrooms', 'bathrooms', 'accepts_pets')
    search_fields = ('title', 'description', 'address', 'owner__email')
    inlines = [PropertyImageInline]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'property', 'status', 'application_date')
    list_filter = ('status', 'application_date')
    search_fields = ('applicant__email', 'property__title')

@admin.register(HouseType)
class HouseTypeAdmin(admin.ModelAdmin):
    list_display = ('id','name',)
    search_fields = ('name',)

@admin.register(HouseLocation)
class HouseLocation(admin.ModelAdmin):
    list_display = ('id','name','city')
    list_filter = ('city',)
    search_fields = ('name','city')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__email', 'receiver__email', 'content')

@admin.register(LeaseAgreement)
class LeaseAgreementAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'start_date', 'end_date', 'rent_amount', 'is_signed')
    list_filter = ('is_signed', 'start_date', 'end_date')
    search_fields = ('tenant__email', 'property__title')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewed', 'property', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__email', 'reviewed__email', 'property__title', 'comment')

# If you want to customize the PropertyImage admin separately
@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'order')
    list_filter = ('property',)
    search_fields = ('property__title',)
# from .models import Site, Niche, LinkRequest, LinkRequestStatus

# @admin.register(Niche)
# class NicheAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)

# @admin.register(Site)
# class SiteAdmin(admin.ModelAdmin):
#     list_display = ('name', 'domain', 'niche', 'domain_authority', 'organic_traffic', 'price_per_link', 'available_slots')
#     list_filter = ('niche', 'support_casino', 'support_sports_betting', 'support_loans', 'support_dating', 'support_forex', 'support_crypto')
#     search_fields = ('name', 'domain')

# @admin.register(LinkRequestStatus)
# class LinkRequestStatusAdmin(admin.ModelAdmin):
#     list_display = ('status', 'timestamp')
#     search_fields = ('status',)

# @admin.register(LinkRequest)
# class LinkRequestAdmin(admin.ModelAdmin):
#     list_display = ('url', 'anchor_text', 'advertiser', 'site', 'status', 'type', 'created_at')
#     list_filter = ('status', 'type', 'created_at')
#     search_fields = ('url', 'anchor_text')
#     readonly_fields = ('created_at', 'updated_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'content', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('property__title', 'tenant__user__email', 'content')
    readonly_fields = ('created_at', 'updated_at')