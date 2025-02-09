from django.contrib import admin
from .models import Property, PropertyImage, Application, Message, LeaseAgreement, Review, HouseType, HouseLocation, Comment, RentPayment


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

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'order')
    list_filter = ('property',)
    search_fields = ('property__title',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('property', 'commenter', 'is_owner', 'content', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('property__title', 'commenter__email', 'content')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'amount', 'due_date', 'payment_date', 'status', 'transaction_id')
    list_filter = (
        'status',
        ('property', admin.RelatedOnlyFieldListFilter),
        ('tenant', admin.RelatedOnlyFieldListFilter),
        'due_date',
        'payment_date',
    )
    search_fields = (
        'property__title',
        'tenant__email',
        'tenant__first_name',
        'tenant__last_name',
        'transaction_id'
    )
    date_hierarchy = 'due_date'
    ordering = ['-due_date']
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'tenant')

