from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import TenantProfile

def upload_to(instance, filename):
    return filename.format(filename=filename)

class Property(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    area = models.PositiveIntegerField(help_text="Area in square feet")
    is_available = models.BooleanField(default=True)
    preferred_lease_term = models.IntegerField(help_text="Preferred lease term in months", blank=True, null=True)
    accepts_pets = models.BooleanField(default=False, blank=True, null=True)
    pet_deposit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    accepts_smokers = models.BooleanField(default=False, blank=True, null=True) 
    pool = models.BooleanField(default=False, blank=True, null=True)
    garden = models.BooleanField(default=False, blank=True, null=True)
    type = models.ForeignKey('HouseType', on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey('HouseLocation', on_delete=models.CASCADE, null=True, blank=True) 
    main_image = models.ForeignKey('PropertyImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    tenants_with_access = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='properties_with_access')
    current_tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='current_tenant')

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

    # def clean(self):
    #     if self.images.count() >= 10:
    #         raise ValidationError("Cannot add more than 10 images to a property.")

    @property
    def tenant_comments(self):
        return self.comments.filter(tenant__tenantprofile__isnull=False)

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=upload_to)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['property']),
        ]
        ordering = ['order']

    def __str__(self):
        return f"{self.property.title} - Image {self.order}"
    

class HouseType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class HouseLocation(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.name



class Application(models.Model):
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ], default='PENDING')
    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.applicant.email


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['receiver']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.sender.email} to {self.receiver.email}"


class LeaseAgreement(models.Model):
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lease_agreements')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_signed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['property']),
        ]

    def __str__(self):
        return f"{self.tenant.email} - {self.property.title}"


class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['reviewer']),
            models.Index(fields=['reviewed']),
            models.Index(fields=['property']),
        ]

    def __str__(self):
        return f"{self.reviewer.email} - {self.reviewed.email}"










# class Site(models.Model):
#     publisher = models.ForeignKey(PublisherProfile, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255)
#     domain = models.CharField(max_length=255, unique=True)
#     niche = models.ForeignKey('Niche', on_delete=models.CASCADE)
#     domain_authority = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
#     organic_traffic = models.PositiveIntegerField()
#     price_per_link = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
#     available_slots = models.PositiveIntegerField(blank=True, null=True)
#     guidelines = models.TextField(blank=True, null=True)
#     support_casino = models.BooleanField(default=False)
#     support_sports_betting = models.BooleanField(default=False)
#     support_loans = models.BooleanField(default=False)
#     support_dating = models.BooleanField(default=False)
#     support_forex = models.BooleanField(default=False)
#     support_crypto = models.BooleanField(default=False)
#     casino_multiplier = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     sports_betting_multiplier = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     loans_multiplier = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     dating_multiplier = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     forex_multiplier = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     crypto_multiplier = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


#     class Meta:
#         indexes = [
#             models.Index(fields=['domain']),
#             models.Index(fields=['niche']),
#         ]

#     def __str__(self):
#         return self.domain
    

# class Niche(models.Model):
#     name = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name


# class LinkRequest(models.Model):
#     advertiser = models.ForeignKey(AdvertiserProfile, on_delete=models.CASCADE)
#     publisher = models.ForeignKey(PublisherProfile, on_delete=models.CASCADE)
#     site = models.ForeignKey(Site, on_delete=models.CASCADE)
#     url = models.URLField()
#     anchor_text = models.CharField(max_length=255)
#     status = models.ForeignKey('LinkRequestStatus', on_delete=models.CASCADE, related_name='link_requests')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     type = models.CharField(max_length=50)
#     category = models.CharField(max_length=50)
#     cost = models.DecimalField(max_digits=10, decimal_places=3)

#     class Meta:
#         indexes = [
#             models.Index(fields=['status']),
#             models.Index(fields=['created_at']),
#         ]

#     def __str__(self):
#         return self.url

# class LinkRequestStatus(models.Model):
#     status = models.CharField(max_length=50,)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-timestamp']
#         indexes = [
#             models.Index(fields=['timestamp']),
#         ]


# class Payment(models.Model):
#     request = models.ForeignKey(LinkRequest, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     stripe_payment_id = models.CharField(max_length=255)
#     status = models.CharField(max_length=50)
#     created_at = models.DateTimeField(auto_now_add=True)

# class Rating(models.Model):
#     advertiser = models.ForeignKey(AdvertiserProfile, on_delete=models.CASCADE)
#     publisher = models.ForeignKey(PublisherProfile, on_delete=models.CASCADE)
#     rating = models.IntegerField()
#     comment = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

# class Report(models.Model):
#     advertiser = models.ForeignKey(AdvertiserProfile, on_delete=models.CASCADE)
#     publisher = models.ForeignKey(PublisherProfile, on_delete=models.CASCADE)
#     reason = models.TextField()
#     status = models.CharField(max_length=50)
#     created_at = models.DateTimeField(auto_now_add=True)
#     resolved_at = models.DateTimeField(null=True, blank=True)




class Comment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments')
    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='property_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['tenant']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.tenant.user.email} on {self.property.title}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not hasattr(self.tenant, 'tenantprofile'):
            raise ValidationError("Only tenants can make comments on properties.")



