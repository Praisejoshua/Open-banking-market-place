"""
URL configuration for the loans app.
"""
from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    # Loan Products (Public)
    path('products/', views.LoanProductListView.as_view(), name='product_list'),
    path('products/<uuid:pk>/', views.LoanProductDetailView.as_view(), name='product_detail'),
    
    # Borrower Views
    path('apply/', views.apply_for_loan, name='apply'),
    path('apply/<uuid:product_id>/', views.apply_for_loan, name='apply_with_product'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<uuid:pk>/', views.application_detail, name='application_detail'),
    path('offers/<uuid:offer_id>/accept/', views.accept_offer, name='accept_offer'),
    path('offers/<uuid:offer_id>/decline/', views.decline_offer, name='decline_offer'),
    
    # Lender Views
    path('lender/products/', views.lender_products, name='lender_products'),
    path('lender/products/create/', views.create_product, name='create_product'),
    path('lender/products/<uuid:pk>/edit/', views.edit_product, name='edit_product'),
    path('lender/applications/', views.incoming_applications, name='incoming_applications'),
    path('lender/applications/<uuid:pk>/review/', views.review_application, name='review_application'),
    path('lender/applications/<uuid:application_id>/offer/', views.make_offer, name='make_offer'),
    
    # Credit Score
    path('credit-score/', views.credit_score_view, name='credit_score'),
    
    # AJAX
    path('ajax/calculate/', views.calculate_loan, name='calculate_loan'),
]
