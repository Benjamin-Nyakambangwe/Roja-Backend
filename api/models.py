from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import TenantProfile
from django.contrib.auth import get_user_model
from django.utils import timezone


def upload_to(instance, filename):
    return filename.format(filename=filename)


class Property(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    area = models.PositiveIntegerField(help_text="Area in square feet")
    is_available = models.BooleanField(default=True)
    preferred_lease_term = models.IntegerField(
        help_text="Preferred lease term in months", blank=True, null=True)
    accepts_pets = models.BooleanField(default=False, blank=True, null=True)
    pet_deposit = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    accepts_smokers = models.BooleanField(default=False, blank=True, null=True)
    pool = models.BooleanField(default=False, blank=True, null=True)
    garden = models.BooleanField(default=False, blank=True, null=True)
    has_solar_power = models.BooleanField(default=False, blank=True, null=True)
    has_borehole = models.BooleanField(default=False, blank=True, null=True)
    type = models.ForeignKey(
        'HouseType', on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(
        'HouseLocation', on_delete=models.CASCADE, null=True, blank=True)
    main_image = models.ForeignKey(
        'PropertyImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    tenants_with_access = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='properties_with_access')
    current_tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='current_tenant')
    previous_tenants_with_access = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='previous_properties_with_access')
    previous_tenants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='previous_properties')
    accepts_in_app_payment = models.BooleanField(default=False)
    accepts_cash_payment = models.BooleanField(default=False)
    proof_of_residence = models.FileField(
        upload_to=upload_to, null=True, blank=True)
    affidavit = models.FileField(upload_to=upload_to, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    overall_rating = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['title']),
            models.Index(fields=['-overall_rating']),
        ]
        ordering = ['-overall_rating', '-id']

    def __str__(self):
        return self.title

    @property
    def tenant_comments(self):
        return self.comments.filter(tenant__tenantprofile__isnull=False)


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='images')
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
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ], default='PENDING')
    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.applicant.email


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.email} to {self.receiver.email}"


class LeaseAgreement(models.Model):
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lease_agreements')
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
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
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


class Comment(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_reply = models.BooleanField(default=False)
    is_rated = models.BooleanField(default=False)
    ai_rating = models.FloatField(null=True, blank=True, default=0.00)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='comment_likes', blank=True)
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='comment_dislikes', blank=True)

    def __str__(self):
        return f"Comment by {self.commenter.email} on {self.property.title}"

    def get_like_count(self):
        return self.likes.count()

    def get_dislike_count(self):
        return self.dislikes.count()

    def has_user_liked(self, user):
        return self.likes.filter(id=user.id).exists()

    def has_user_disliked(self, user):
        return self.dislikes.filter(id=user.id).exists()

    def toggle_like(self, user):
        """Toggle like for a user on this comment"""
        if self.has_user_liked(user):
            self.likes.remove(user)
            return False
        else:
            if self.has_user_disliked(user):
                self.dislikes.remove(user)
            self.likes.add(user)
            return True

    def toggle_dislike(self, user):
        """Toggle dislike for a user on this comment"""
        if self.has_user_disliked(user):
            self.dislikes.remove(user)
            return False
        else:
            if self.has_user_liked(user):
                self.likes.remove(user)
            self.dislikes.add(user)
            return True


# class Comment(models.Model):
#     property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments')
#     tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE, related_name='property_comments')
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['property']),
#             models.Index(fields=['tenant']),
#             models.Index(fields=['created_at']),
#         ]

#     def __str__(self):
#         return f"Comment by {self.tenant.user.email} on {self.property.title}"

#     def clean(self):
#         from django.core.exceptions import ValidationError
#         if not hasattr(self.tenant, 'tenantprofile'):
#             raise ValidationError("Only tenants can make comments on properties.")


class RentPayment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='rent_payments')
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rent_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['property', 'tenant']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.property.title} - {self.tenant.email} - {self.due_date}"

    def save(self, *args, **kwargs):
        if self.status == 'PENDING' and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)

    def update_landlord_balance(self):
        """Update landlord balance when payment is completed"""
        if self.status == 'PAID':
            landlord = self.property.owner
            from accounts.models import LandlordBalance

            # Get or create landlord balance
            balance, created = LandlordBalance.objects.get_or_create(
                landlord=landlord)

            # Update balance
            balance.amount += self.amount
            balance.save()

            return True
        return False


class PhoneVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(minutes=5)
        return timezone.now() > expiration_time


class LeaseDocumentPayment(models.Model):
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING')
    payment_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lease Document Payment - {self.landlord.email} - {self.status}"

    # def save(self, *args, **kwargs):
    #     # This save method overrides the default save behavior
    #     # If a payment is still PENDING but its due date has passed,
    #     # automatically update its status to OVERDUE before saving
    #     if self.status == 'PENDING' and self.due_date < timezone.now().date():
    #         self.status = 'OVERDUE'

    #     # Call the parent class's save method to actually save the object
    #     super().save(*args, **kwargs)
