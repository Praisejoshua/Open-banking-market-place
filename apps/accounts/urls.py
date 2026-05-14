"""
URL configuration for the accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Landing page
    path('', views.LandingPageView.as_view(), name='landing'),
    
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/upload-document/', views.upload_document, name='upload_document'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    
    # Activity Log
    path('activity-log/', views.activity_log_view, name='activity_log'),
]
