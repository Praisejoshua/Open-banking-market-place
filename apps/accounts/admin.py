"""
Admin configuration for the accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserDocument, ActivityLog, UserPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface."""
    
    list_display = [
        'email', 'username', 'get_full_name', 'role', 'is_active',
        'is_email_verified', 'is_identity_verified', 'date_joined', 'last_activity'
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'is_email_verified', 'is_identity_verified', 'gender']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'bvn']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {
            'fields': ('role', 'phone_number', 'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country')
        }),
        ('Financial Information', {
            'fields': ('annual_income', 'employment_status', 'employer_name', 'job_title', 'years_employed'),
            'classes': ('collapse',)
        }),
        ('Lender Information', {
            'fields': ('company_name', 'company_registration', 'license_number'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_email_verified', 'is_phone_verified', 'is_identity_verified', 'bvn', 'nin')
        }),
        ('Security', {
            'fields': ('two_factor_enabled', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_activity']
    
    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.get_full_name()


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    """Admin for UserDocument model."""
    
    list_display = ['user', 'document_type', 'document_number', 'is_verified', 'uploaded_at']
    list_filter = ['document_type', 'is_verified', 'uploaded_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'document_number']
    ordering = ['-uploaded_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin for ActivityLog model."""
    
    list_display = ['user', 'activity_type', 'description', 'ip_address', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__email', 'description', 'ip_address']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """Admin for UserPreference model."""
    
    list_display = ['user', 'email_notifications', 'sms_notifications', 'language', 'currency']
    search_fields = ['user__email']
