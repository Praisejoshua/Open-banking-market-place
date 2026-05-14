"""
URL configuration for the analytics app.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('overview/', views.system_overview, name='overview'),
    path('users/', views.user_analytics, name='user_analytics'),
    path('loans/', views.loan_analytics, name='loan_analytics'),
]
