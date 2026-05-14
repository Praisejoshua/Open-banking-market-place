"""
Views for the analytics app.
Provides analytics and reporting functionality.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta

from apps.loans.models import LoanApplication, LoanProduct, LoanOffer
from apps.accounts.models import User


@staff_member_required
def system_overview(request):
    """System-wide analytics overview."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # User metrics
    user_metrics = {
        'total_users': User.objects.filter(is_active=True).count(),
        'new_users_30d': User.objects.filter(date_joined__gte=thirty_days_ago).count(),
        'borrowers': User.objects.filter(role='borrower', is_active=True).count(),
        'lenders': User.objects.filter(role='lender', is_active=True).count(),
        'verified_users': User.objects.filter(is_identity_verified=True).count(),
    }
    
    # Loan metrics
    loan_metrics = {
        'total_applications': LoanApplication.objects.count(),
        'applications_30d': LoanApplication.objects.filter(created_at__gte=thirty_days_ago).count(),
        'approved': LoanApplication.objects.filter(status='approved').count(),
        'rejected': LoanApplication.objects.filter(status='rejected').count(),
        'pending': LoanApplication.objects.filter(status__in=['submitted', 'under_review']).count(),
        'total_disbursed': LoanApplication.objects.filter(
            status__in=['disbursed', 'in_repayment', 'completed']
        ).aggregate(total=Sum('amount_approved'))['total'] or 0,
    }
    
    # Product metrics
    product_metrics = {
        'total_products': LoanProduct.objects.count(),
        'active_products': LoanProduct.objects.filter(status='active').count(),
        'featured_products': LoanProduct.objects.filter(is_featured=True).count(),
    }
    
    # Daily application trend (last 30 days)
    daily_stats = []
    for i in range(29, -1, -1):
        date = (now - timedelta(days=i)).date()
        day_start = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
        day_end = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.max.time()))
        
        count = LoanApplication.objects.filter(created_at__range=(day_start, day_end)).count()
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Loan type distribution
    type_distribution = LoanApplication.objects.values('loan_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status distribution
    status_distribution = LoanApplication.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'user_metrics': user_metrics,
        'loan_metrics': loan_metrics,
        'product_metrics': product_metrics,
        'daily_stats': daily_stats,
        'type_distribution': type_distribution,
        'status_distribution': status_distribution,
    }
    return render(request, 'analytics/system_overview.html', context)


@staff_member_required
def user_analytics(request):
    """User-related analytics."""
    # Registration trend
    months = []
    borrower_counts = []
    lender_counts = []
    
    for i in range(5, -1, -1):
        month_start = timezone.now() - timedelta(days=30*i)
        month_label = month_start.strftime('%b %Y')
        months.append(month_label)
        
        borrower_counts.append(
            User.objects.filter(role='borrower', date_joined__month=month_start.month).count()
        )
        lender_counts.append(
            User.objects.filter(role='lender', date_joined__month=month_start.month).count()
        )
    
    # Role distribution
    role_distribution = User.objects.values('role').annotate(
        count=Count('id')
    )
    
    context = {
        'months': months,
        'borrower_counts': borrower_counts,
        'lender_counts': lender_counts,
        'role_distribution': role_distribution,
    }
    return render(request, 'analytics/user_analytics.html', context)


@staff_member_required
def loan_analytics(request):
    """Loan-related analytics."""
    # Amount distribution
    amount_ranges = [
        ('0-50K', 0, 50000),
        ('50K-100K', 50000, 100000),
        ('100K-500K', 100000, 500000),
        ('500K-1M', 500000, 1000000),
        ('1M+', 1000000, float('inf')),
    ]
    
    amount_distribution = []
    for label, min_amount, max_amount in amount_ranges:
        if max_amount == float('inf'):
            count = LoanApplication.objects.filter(amount_requested__gte=min_amount).count()
        else:
            count = LoanApplication.objects.filter(
                amount_requested__gte=min_amount,
                amount_requested__lt=max_amount
            ).count()
        amount_distribution.append({'label': label, 'count': count})
    
    # Average loan by type
    avg_by_type = LoanApplication.objects.values('loan_type').annotate(
        avg_amount=Avg('amount_requested'),
        count=Count('id')
    ).order_by('-avg_amount')
    
    context = {
        'amount_distribution': amount_distribution,
        'avg_by_type': avg_by_type,
    }
    return render(request, 'analytics/loan_analytics.html', context)
