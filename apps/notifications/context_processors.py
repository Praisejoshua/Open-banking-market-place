"""
Context processor for notifications.
Adds unread notification count to template context.
"""
from .services import NotificationService


def notification_count(request):
    """Add unread notification count to context."""
    if request.user.is_authenticated:
        count = NotificationService.get_unread_count(request.user)
        recent_notifications = request.user.notifications.filter(
            is_read=False
        ).order_by('-created_at')[:5]
        return {
            'unread_notification_count': count,
            'recent_notifications': recent_notifications,
        }
    return {
        'unread_notification_count': 0,
        'recent_notifications': [],
    }
