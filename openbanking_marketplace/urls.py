"""
URL configuration for Open Banking Marketplace Application.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls', namespace='accounts')),
    path('loans/', include('apps.loans.urls', namespace='loans')),
    path('marketplace/', include('apps.marketplace.urls', namespace='marketplace')),
    path('banking/', include('apps.banking.urls', namespace='banking')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
