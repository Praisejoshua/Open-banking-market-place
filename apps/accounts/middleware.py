"""
Middleware for the accounts app.
"""
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class UserActivityMiddleware(MiddlewareMixin):
    """Update user's last activity timestamp on each request."""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Update last activity every 5 minutes to avoid excessive DB writes
            if (not request.user.last_activity or 
                (timezone.now() - request.user.last_activity).total_seconds() > 300):
                request.user.last_activity = timezone.now()
                request.user.save(update_fields=['last_activity'])
        return None
