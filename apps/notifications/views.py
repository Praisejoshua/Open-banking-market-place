"""
Views for the notifications app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Notification
from .services import NotificationService


@login_required
def notification_list(request):
    """List all notifications for the user."""
    notifications = request.user.notifications.all()
    
    # Filter by read status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)
    
    context = {
        'notifications': notifications,
        'filter_type': filter_type,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_read(request, notification_id):
    """Mark a notification as read."""
    if request.method == 'POST':
        success = NotificationService.mark_as_read(notification_id, request.user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': success})
        if success:
            messages.success(request, 'Notification marked as read.')
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Mark all notifications as read."""
    if request.method == 'POST':
        NotificationService.mark_all_as_read(request.user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')
