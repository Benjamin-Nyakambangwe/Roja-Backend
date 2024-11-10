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
    previous_tenants_with_access = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='previous_properties_with_access')
    previous_tenants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='previous_properties')
    accepts_in_app_payment = models.BooleanField(default=False)
    accepts_cash_payment = models.BooleanField(default=False)
    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

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
        ordering = ['timestamp']

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


class Comment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='property_comments',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_owner = models.BooleanField(default=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_comments', blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['commenter']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.commenter.email} on {self.property.title}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not (hasattr(self.commenter, 'tenantprofile') or self.property.owner == self.commenter):
            raise ValidationError("Only tenants or the property owner can make comments on properties.")

    def get_like_count(self):
        """
        Get the number of likes for this comment
        """
        return self.likes.count()

    def get_dislike_count(self):
        """
        Get the number of dislikes for this comment
        """
        return self.dislikes.count()

    def toggle_like(self, user):
        """
        Toggle like for a comment. Remove dislike if exists.
        """
        print(f"Toggle like called for user {user.email} on comment {self.id}")
        if user in self.likes.all():
            print(f"User {user.email} already liked comment {self.id}, removing like")
            self.likes.remove(user)
            return False
        else:
            print(f"User {user.email} liking comment {self.id}")
            self.dislikes.remove(user)  # Remove dislike if exists
            self.likes.add(user)
            return True

    def toggle_dislike(self, user):
        """
        Toggle dislike for a comment. Remove like if exists.
        """
        if user in self.dislikes.all():
            self.dislikes.remove(user)
            return False
        else:
            self.likes.remove(user)  # Remove like if exists
            self.dislikes.add(user)
            return True

    def has_user_liked(self, user):
        """
        Check if a user has liked the comment
        """
        return user in self.likes.all()

    def has_user_disliked(self, user):
        """
        Check if a user has disliked the comment
        """
        return user in self.dislikes.all()










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

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rent_payments')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rent_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
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




