"""
URL configuration for the banking app.
"""
from django.urls import path
from . import views

app_name = 'banking'

urlpatterns = [
    path('accounts/', views.linked_accounts, name='linked_accounts'),
    path('accounts/link/', views.link_account, name='link_account'),
    path('accounts/<uuid:pk>/', views.account_detail, name='account_detail'),
    path('accounts/<uuid:pk>/disconnect/', views.disconnect_account, name='disconnect_account'),
    path('transactions/', views.transactions, name='transactions'),
]
