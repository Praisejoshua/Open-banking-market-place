"""
Accounts models for Open Banking Marketplace.
Implements custom User model with role-based access control.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    Supports Borrower, Lender, and Administrator roles.
    """
    
    ROLE_CHOICES = [
        ('borrower', 'Borrower'),
        ('lender', 'Lender'),
        ('admin', 'Administrator'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='Email Address')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='borrower')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Enter a valid phone number.')],
        blank=True,
        verbose_name='Phone Number'
    )
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Date of Birth')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True, verbose_name='Residential Address')
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Nigeria')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Financial profile (for borrowers)
    annual_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    employment_status = models.CharField(max_length=50, blank=True, choices=[
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('retired', 'Retired'),
        ('business_owner', 'Business Owner'),
    ])
    employer_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    years_employed = models.PositiveIntegerField(null=True, blank=True)
    
    # Lender profile
    company_name = models.CharField(max_length=200, blank=True)
    company_registration = models.CharField(max_length=100, blank=True, verbose_name='Registration Number')
    license_number = models.CharField(max_length=100, blank=True)
    
    # Verification
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_identity_verified = models.BooleanField(default=False)
    bvn = models.CharField(max_length=11, blank=True, verbose_name='Bank Verification Number')
    nin = models.CharField(max_length=11, blank=True, verbose_name='National Identity Number')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Two-factor authentication
    two_factor_enabled = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def is_borrower(self):
        return self.role == 'borrower'
    
    @property
    def is_lender(self):
        return self.role == 'lender'
    
    @property
    def is_administrator(self):
        return self.role == 'admin'
    
    @property
    def profile_completion(self):
        """Calculate profile completion percentage."""
        required_fields = [
            self.first_name, self.last_name, self.phone_number,
            self.date_of_birth, self.address, self.city, self.state,
            self.annual_income, self.employment_status
        ]
        if not required_fields:
            return 0
        return int((sum(1 for f in required_fields if f) / len(required_fields)) * 100)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class UserDocument(models.Model):
    """Documents uploaded by users for verification."""
    
    DOCUMENT_TYPES = [
        ('id_card', 'National ID Card'),
        ('passport', 'International Passport'),
        ('drivers_license', "Driver's License"),
        ('utility_bill', 'Utility Bill'),
        ('bank_statement', 'Bank Statement'),
        ('payslip', 'Payslip'),
        ('tax_return', 'Tax Return'),
        ('cac_certificate', 'CAC Certificate'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='documents/%Y/%m/')
    document_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Document'
        verbose_name_plural = 'User Documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_document_type_display()}"


class ActivityLog(models.Model):
    """Track user activities for security and audit purposes."""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
        ('loan_application', 'Loan Application'),
        ('document_upload', 'Document Upload'),
        ('bank_link', 'Bank Account Linked'),
        ('offer_accepted', 'Loan Offer Accepted'),
        ('payment', 'Payment Made'),
        ('settings_change', 'Settings Change'),
        ('failed_login', 'Failed Login Attempt'),
        ('suspicious_activity', 'Suspicious Activity'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} at {self.timestamp}"


class UserPreference(models.Model):
    """User preferences and settings."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    two_factor_method = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('app', 'Authenticator App')],
        default='email'
    )
    language = models.CharField(max_length=10, default='en')
    currency = models.CharField(max_length=10, default='NGN')
    timezone = models.CharField(max_length=50, default='Africa/Lagos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.email}"
