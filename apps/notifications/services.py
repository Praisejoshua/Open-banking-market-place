"""
Notification service for creating and managing notifications.
"""
from django.utils import timezone
from .models import Notification


class NotificationService:
    """Service class for creating and managing notifications."""
    
    @staticmethod
    def create_notification(user, notification_type, title, message,
                           related_object=None, priority='normal',
                           action_url='', action_text=''):
        """
        Create a new notification for a user.
        
        Args:
            user: The user to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            related_object: Related object (optional)
            priority: Notification priority
            action_url: URL for action button
            action_text: Text for action button
        """
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
            action_text=action_text or 'View Details'
        )
        
        # Set related object info
        if related_object:
            notification.related_object_type = related_object.__class__.__name__
            notification.related_object_id = str(related_object.id)
            
            # Auto-generate action URL
            if not action_url:
                notification.action_url = NotificationService._get_object_url(related_object)
            
            notification.save()
        
        return notification
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark a notification as read."""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user."""
        Notification.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for a user."""
        return Notification.objects.filter(user=user, is_read=False).count()
    
    @staticmethod
    def _get_object_url(obj):
        """Generate URL for a related object."""
        class_name = obj.__class__.__name__
        
        if class_name == 'LoanApplication':
            return f'/loans/applications/{obj.id}/'
        elif class_name == 'LoanOffer':
            return f'/loans/applications/{obj.application.id}/'
        elif class_name == 'LoanProduct':
            return f'/loans/products/{obj.id}/'
        elif class_name == 'BankAccount':
            return f'/banking/accounts/{obj.id}/'
        return ''
