"""
URL configuration for the marketplace app.
"""
from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('compare/', views.compare_products, name='compare'),
]
