"""
Views for the marketplace app.
Handles dashboards and main marketplace functionality.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta

from apps.loans.models import LoanProduct, LoanApplication, LoanOffer
from apps.accounts.models import User


@login_required
def dashboard(request):
    """Main dashboard view - redirects based on user role."""
    if request.user.is_borrower:
        return borrower_dashboard(request)
    elif request.user.is_lender:
        return lender_dashboard(request)
    else:
        return admin_dashboard(request)


def borrower_dashboard(request):
    """Borrower dashboard with loan applications and offers."""
    user = request.user
    
    # Get recent applications
    recent_applications = LoanApplication.objects.filter(
        borrower=user
    ).select_related('loan_product').order_by('-created_at')[:5]
    
    # Get pending offers
    pending_offers = LoanOffer.objects.filter(
        application__borrower=user,
        status='pending',
        expires_at__gt=timezone.now()
    ).select_related('lender', 'loan_product', 'application').order_by('-created_at')[:5]
    
    # Get active loans
    active_loans = LoanApplication.objects.filter(
        borrower=user,
        status__in=['offer_accepted', 'disbursed', 'in_repayment']
    )
    
    # Get credit score
    credit_score = None
    try:
        credit_score = user.credit_score_record
    except:
        pass
    
    # Quick stats
    total_applied = LoanApplication.objects.filter(borrower=user).count()
    total_approved = LoanApplication.objects.filter(borrower=user, status='approved').count()
    total_active = active_loans.count()
    
    # Featured products
    featured_products = LoanProduct.objects.filter(
        status='active',
        is_featured=True
    ).select_related('lender')[:4]
    
    context = {
        'recent_applications': recent_applications,
        'pending_offers': pending_offers,
        'active_loans': active_loans,
        'credit_score': credit_score,
        'total_applied': total_applied,
        'total_approved': total_approved,
        'total_active': total_active,
        'featured_products': featured_products,
    }
    return render(request, 'marketplace/borrower_dashboard.html', context)


def lender_dashboard(request):
    """Lender dashboard with applications and product performance."""
    user = request.user
    
    # Product stats
    total_products = LoanProduct.objects.filter(lender=user).count()
    active_products = LoanProduct.objects.filter(lender=user, status='active').count()
    
    # Application stats
    incoming_apps = LoanApplication.objects.filter(
        loan_product__lender=user,
        status__in=['submitted', 'under_review']
    ).count()
    
    total_apps = LoanApplication.objects.filter(loan_product__lender=user).count()
    approved_apps = LoanApplication.objects.filter(
        loan_product__lender=user,
        status='approved'
    ).count()
    
    # Recent applications
    recent_applications = LoanApplication.objects.filter(
        loan_product__lender=user
    ).select_related('borrower', 'loan_product').order_by('-created_at')[:10]
    
    # Total amount disbursed
    total_disbursed = LoanApplication.objects.filter(
        loan_product__lender=user,
        status__in=['disbursed', 'in_repayment', 'completed']
    ).aggregate(total=Sum('amount_approved'))['total'] or 0
    
    # Monthly applications trend (last 6 months)
    months = []
    app_counts = []
    for i in range(5, -1, -1):
        month_start = timezone.now() - timedelta(days=30*i)
        month_label = month_start.strftime('%b')
        months.append(month_label)
        count = LoanApplication.objects.filter(
            loan_product__lender=user,
            created_at__month=month_start.month,
            created_at__year=month_start.year
        ).count()
        app_counts.append(count)
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'incoming_apps': incoming_apps,
        'total_apps': total_apps,
        'approved_apps': approved_apps,
        'recent_applications': recent_applications,
        'total_disbursed': total_disbursed,
        'months': months,
        'app_counts': app_counts,
    }
    return render(request, 'marketplace/lender_dashboard.html', context)


def admin_dashboard(request):
    """Administrator dashboard with system overview."""
    # User statistics
    total_users = User.objects.filter(is_active=True).count()
    total_borrowers = User.objects.filter(role='borrower', is_active=True).count()
    total_lenders = User.objects.filter(role='lender', is_active=True).count()
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()
    
    # Loan statistics
    total_applications = LoanApplication.objects.count()
    pending_applications = LoanApplication.objects.filter(
        status__in=['submitted', 'under_review']
    ).count()
    approved_applications = LoanApplication.objects.filter(status='approved').count()
    total_disbursed = LoanApplication.objects.filter(
        status__in=['disbursed', 'in_repayment', 'completed']
    ).aggregate(total=Sum('amount_approved'))['total'] or 0
    
    # Product statistics
    total_products = LoanProduct.objects.count()
    active_products = LoanProduct.objects.filter(status='active').count()
    
    # Recent activity
    recent_applications = LoanApplication.objects.select_related(
        'borrower', 'loan_product'
    ).order_by('-created_at')[:10]
    
    # Applications by status
    status_distribution = LoanApplication.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Monthly trend
    months = []
    app_counts = []
    for i in range(5, -1, -1):
        month_start = timezone.now() - timedelta(days=30*i)
        month_label = month_start.strftime('%b %Y')
        months.append(month_label)
        count = LoanApplication.objects.filter(
            created_at__month=month_start.month,
            created_at__year=month_start.year
        ).count()
        app_counts.append(count)
    
    context = {
        'total_users': total_users,
        'total_borrowers': total_borrowers,
        'total_lenders': total_lenders,
        'new_users_today': new_users_today,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'total_disbursed': total_disbursed,
        'total_products': total_products,
        'active_products': active_products,
        'recent_applications': recent_applications,
        'status_distribution': status_distribution,
        'months': months,
        'app_counts': app_counts,
    }
    return render(request, 'marketplace/admin_dashboard.html', context)


@login_required
def compare_products(request):
    """Compare loan products side by side."""
    product_ids = request.GET.getlist('product')
    products = LoanProduct.objects.filter(id__in=product_ids, status='active').select_related('lender')
    
    context = {
        'products': products,
    }
    return render(request, 'marketplace/compare.html', context)
