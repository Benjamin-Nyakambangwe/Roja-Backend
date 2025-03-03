from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid


def upload_to(instance, filename):
    return filename.format(filename=filename)


class UserAccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, user_type, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name,
                          last_name=last_name, user_type=user_type, **extra_fields)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, user_type, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, user_type, password, **extra_fields)


class UserAccount(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    )

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default='landlord')
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    last_login = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email


class LandlordProfile(models.Model):
    user = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, related_name='landlord_profile')

    # Personal Information
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Communication Preferences
    emergency_contact_name = models.CharField(
        max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(
        max_length=15, blank=True, null=True)
    # Additional Information
    additional_notes = models.TextField(blank=True, null=True)
    # Profile Status
    is_profile_complete = models.BooleanField(
        default=False, blank=True, null=True)
    is_verified = models.BooleanField(default=False, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    id_image = models.FileField(upload_to=upload_to, null=True, blank=True)
    profile_image = models.ImageField(
        upload_to=upload_to, null=True, blank=True)
    id_number = models.CharField(max_length=100, blank=True, null=True)
    proof_of_residence = models.FileField(
        upload_to=upload_to, null=True, blank=True)
    marital_status = models.CharField(max_length=100, blank=True, null=True)
    is_phone_verified = models.BooleanField(
        default=False, blank=True, null=True)
    current_rating = models.DecimalField(
        max_digits=3, decimal_places=2, blank=True, null=True, default=0.00)

    def __str__(self):
        return f"Landlord Profile: {self.user.email}"


class TenantProfile(models.Model):
    user = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, related_name='tenant_profile')
    # Personal Information
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(
        max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(
        max_length=15, blank=True, null=True)
    # Additional Personal Details
    occupation = models.CharField(max_length=100, blank=True, null=True)
    employer = models.CharField(max_length=100, blank=True, null=True)
    work_phone = models.CharField(max_length=15, blank=True, null=True)
    # Preferences
    preferred_lease_term = models.IntegerField(
        blank=True, null=True, help_text="Preferred lease term in months")
    max_rent = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    preferred_move_in_date = models.DateField(blank=True, null=True)
    preferred_area = models.TextField(
        blank=True, null=True, help_text="Comma-separated list of preferred areas")
    # Additional Information
    number_of_occupants = models.IntegerField(blank=True, null=True)
    pets = models.BooleanField(default=False, blank=True, null=True)
    pet_details = models.TextField(blank=True, null=True)
    smoker = models.BooleanField(default=False, blank=True, null=True)
    has_vehicle = models.BooleanField(default=False, blank=True, null=True)
    num_of_vehicles = models.IntegerField(null=True, blank=True)
    # Financial Information
    criminal_record = models.BooleanField(default=False, blank=True, null=True)
    # References
    personal_reference_1_name = models.CharField(
        max_length=100, blank=True, null=True)
    personal_reference_1_phone = models.CharField(
        max_length=15, blank=True, null=True)
    personal_reference_1_relation = models.CharField(
        max_length=50, blank=True, null=True)
    personal_reference_2_name = models.CharField(
        max_length=100, blank=True, null=True)
    personal_reference_2_phone = models.CharField(
        max_length=15, blank=True, null=True)
    personal_reference_2_relation = models.CharField(
        max_length=50, blank=True, null=True)

    next_of_kin_name = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=15, blank=True, null=True)
    next_of_kin_email = models.EmailField(blank=True, null=True)
    next_of_kin_relation = models.CharField(
        max_length=50, blank=True, null=True)
    next_of_kin_address = models.TextField(blank=True, null=True)
    # Additional Notes
    additional_notes = models.TextField(blank=True, null=True)
    id_image = models.FileField(upload_to=upload_to, null=True, blank=True)
    profile_image = models.ImageField(
        upload_to=upload_to, null=True, blank=True)
    id_number = models.CharField(max_length=100, blank=True, null=True)
    proof_of_employment = models.FileField(
        upload_to=upload_to, null=True, blank=True)
    marital_status = models.CharField(max_length=100, blank=True, null=True)
    is_phone_verified = models.BooleanField(
        default=False, blank=True, null=True)

    # Profile Status
    is_profile_complete = models.BooleanField(
        default=False, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    pricing_tier = models.ForeignKey(
        'PricingTier', on_delete=models.CASCADE, blank=True, null=True)
    num_properties = models.IntegerField(blank=True, null=True)

    subscription_plan = models.CharField(max_length=100, blank=True, null=True)
    subscription_status = models.CharField(
        max_length=100, blank=True, null=True)
    current_rating = models.DecimalField(
        max_digits=3, decimal_places=2, blank=True, null=True, default=0.00)

    def __str__(self):
        return f"Tenant Profile: {self.user.email}"


class TenantRating(models.Model):
    tenant = models.ForeignKey(
        TenantProfile, on_delete=models.CASCADE, related_name='tenant_ratings')
    landlord = models.ForeignKey(
        LandlordProfile, on_delete=models.CASCADE, related_name='landlord_ratings')
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, blank=True, null=True, default=0.00)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Add this to ensure one landlord can only rate a tenant once
        unique_together = ('tenant', 'landlord')

    def __str__(self):
        return f"Tenant Rating: {self.tenant.user.email}"


class PricingTier(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    max_properties = models.IntegerField(blank=True, null=True)
    max_property_price = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)
    target = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    tenant = models.ForeignKey(
        TenantProfile, on_delete=models.CASCADE, null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)
    poll_url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Initiated')
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.status}"


class LandlordBalance(models.Model):
    landlord = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, related_name='balance')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.landlord.email}: ${self.amount}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected')
    )

    landlord = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reference = models.CharField(max_length=100, unique=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        UserAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_withdrawals')
    notes = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.landlord.email}: ${self.amount} - {self.status}"

    def save(self, *args, **kwargs):
        # Generate reference if not present
        if not self.reference:
            self.reference = f"WD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


@receiver(post_save, sender=UserAccount)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'landlord':
            LandlordProfile.objects.create(user=instance)
        elif instance.user_type == 'tenant':
            TenantProfile.objects.create(user=instance)


@receiver(post_save, sender=UserAccount)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 'landlord':
        instance.landlord_profile.save()
    elif instance.user_type == 'tenant':
        instance.tenant_profile.save()
