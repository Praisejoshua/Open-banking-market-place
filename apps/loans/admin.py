"""
Admin configuration for the loans app.
"""
from django.contrib import admin
from .models import LoanProduct, LoanApplication, CreditScore, LoanOffer, LoanRepayment


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    """Admin for LoanProduct model."""
    
    list_display = [
        'name', 'lender', 'loan_type', 'interest_rate_display',
        'amount_range', 'status', 'is_featured', 'created_at'
    ]
    list_filter = ['status', 'loan_type', 'is_featured', 'requires_collateral']
    search_fields = ['name', 'description', 'lender__email', 'lender__company_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    """Admin for LoanApplication model."""
    
    list_display = [
        'id', 'borrower', 'loan_type', 'amount_requested',
        'status', 'credit_score', 'risk_category', 'created_at'
    ]
    list_filter = ['status', 'loan_type', 'risk_category']
    search_fields = [
        'borrower__email', 'borrower__first_name', 'borrower__last_name',
        'purpose', 'id'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'submitted_at']


@admin.register(CreditScore)
class CreditScoreAdmin(admin.ModelAdmin):
    """Admin for CreditScore model."""
    
    list_display = [
        'user', 'total_score', 'risk_category', 'risk_level',
        'default_probability', 'computed_at'
    ]
    list_filter = ['risk_category', 'risk_level']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-computed_at']
    readonly_fields = ['computed_at']


@admin.register(LoanOffer)
class LoanOfferAdmin(admin.ModelAdmin):
    """Admin for LoanOffer model."""
    
    list_display = [
        'application', 'lender', 'amount_offered',
        'interest_rate', 'status', 'created_at', 'expires_at'
    ]
    list_filter = ['status']
    search_fields = [
        'application__borrower__email',
        'lender__email', 'lender__company_name'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    """Admin for LoanRepayment model."""
    
    list_display = [
        'application', 'installment_number', 'amount_due',
        'amount_paid', 'due_date', 'status'
    ]
    list_filter = ['status']
    search_fields = ['application__borrower__email']
    ordering = ['application', 'installment_number']
