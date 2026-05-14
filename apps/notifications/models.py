"""
Notifications models for Open Banking Marketplace.
"""
import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """User notifications."""
    
    NOTIFICATION_TYPES = [
        ('loan_approved', 'Loan Approved'),
        ('loan_rejected', 'Loan Rejected'),
        ('new_offer', 'New Loan Offer'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
        ('payment_due', 'Payment Due'),
        ('payment_received', 'Payment Received'),
        ('document_verified', 'Document Verified'),
        ('profile_update', 'Profile Update'),
        ('security_alert', 'Security Alert'),
        ('system', 'System Notification'),
        ('promotional', 'Promotional'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related object
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.CharField(max_length=100, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Priority
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Actions
    action_url = models.CharField(max_length=500, blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
