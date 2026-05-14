"""
Views for the loans app.
Handles loan applications, products, credit scoring, and loan offers.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.http import JsonResponse
from decimal import Decimal

from .models import LoanProduct, LoanApplication, CreditScore, LoanOffer, LoanRepayment
from .forms import (
    LoanApplicationForm, LoanProductForm, LoanOfferForm,
    LoanApplicationReviewForm, ApplicationFilterForm
)
from apps.accounts.models import ActivityLog
from apps.notifications.services import NotificationService


# ============== LOAN PRODUCTS ==============

class LoanProductListView(ListView):
    """List all active loan products."""
    model = LoanProduct
    template_name = 'loans/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = LoanProduct.objects.filter(status='active')
        
        # Filter by loan type
        loan_type = self.request.GET.get('loan_type')
        if loan_type:
            queryset = queryset.filter(loan_type=loan_type)
        
        # Filter by amount range
        min_amount = self.request.GET.get('min_amount')
        if min_amount:
            queryset = queryset.filter(max_amount__gte=min_amount)
        
        max_amount = self.request.GET.get('max_amount')
        if max_amount:
            queryset = queryset.filter(min_amount__lte=max_amount)
        
        # Filter by interest rate
        max_rate = self.request.GET.get('max_rate')
        if max_rate:
            queryset = queryset.filter(interest_rate__lte=max_rate)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(lender__company_name__icontains=search)
            )
        
        return queryset.select_related('lender')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loan_types'] = LoanProduct.LOAN_TYPE_CHOICES
        return context


class LoanProductDetailView(DetailView):
    """Detail view for a loan product."""
    model = LoanProduct
    template_name = 'loans/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        product.views_count += 1
        product.save(update_fields=['views_count'])
        
        # Check if user can apply
        if self.request.user.is_authenticated and self.request.user.is_borrower:
            context['can_apply'] = True
            context['has_pending_application'] = LoanApplication.objects.filter(
                borrower=self.request.user,
                status__in=['draft', 'submitted', 'under_review', 'credit_check']
            ).exists()
        
        return context


# ============== BORROWER VIEWS ==============

@login_required
def apply_for_loan(request, product_id=None):
    """Handle loan application submission."""
    if not request.user.is_borrower:
        messages.error(request, 'Only borrowers can apply for loans.')
        return redirect('marketplace:dashboard')
    
    loan_product = None
    if product_id:
        loan_product = get_object_or_404(LoanProduct, id=product_id, status='active')
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.borrower = request.user
            application.loan_product = loan_product
            application.status = 'submitted'
            application.submitted_at = timezone.now()
            
            # Copy user's income if available
            if request.user.annual_income and not application.monthly_income:
                application.monthly_income = request.user.annual_income / 12
            
            application.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                activity_type='loan_application',
                description=f'Loan application #{str(application.id)[:8]} submitted for {application.get_loan_type_display()}'
            )
            
            # Trigger credit scoring
            from .credit_engine import CreditScoringEngine
            engine = CreditScoringEngine()
            engine.score_application(application)
            
            # Update product stats
            if loan_product:
                loan_product.applications_count += 1
                loan_product.save(update_fields=['applications_count'])
            
            messages.success(request, 'Your loan application has been submitted successfully!')
            return redirect('loans:application_detail', pk=application.id)
    else:
        initial = {}
        if loan_product:
            initial = {
                'loan_type': loan_product.loan_type,
                'amount_requested': loan_product.min_amount,
                'duration_months': loan_product.min_duration_months,
            }
        if request.user.annual_income:
            initial['monthly_income'] = request.user.annual_income / 12
        
        form = LoanApplicationForm(initial=initial)
    
    context = {
        'form': form,
        'loan_product': loan_product,
    }
    return render(request, 'loans/apply.html', context)


@login_required
def my_applications(request):
    """List borrower's loan applications."""
    if not request.user.is_borrower:
        messages.error(request, 'Access denied.')
        return redirect('marketplace:dashboard')
    
    applications = LoanApplication.objects.filter(borrower=request.user).select_related('loan_product')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    context = {
        'applications': applications,
        'status_choices': LoanApplication.STATUS_CHOICES,
        'current_filter': status_filter or 'all',
    }
    return render(request, 'loans/my_applications.html', context)


@login_required
def application_detail(request, pk):
    """View loan application details."""
    application = get_object_or_404(LoanApplication, id=pk)
    
    # Check permissions
    if request.user != application.borrower and not request.user.is_lender and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this application.')
        return redirect('marketplace:dashboard')
    
    # Get credit score if available
    credit_score = None
    try:
        credit_score = CreditScore.objects.get(user=application.borrower)
    except CreditScore.DoesNotExist:
        pass
    
    # Get offers
    offers = application.offers.filter(status='pending')
    
    # Get repayment schedule if approved
    repayments = application.repayments.all().order_by('installment_number')
    
    context = {
        'application': application,
        'credit_score': credit_score,
        'offers': offers,
        'repayments': repayments,
    }
    return render(request, 'loans/application_detail.html', context)


@login_required
def accept_offer(request, offer_id):
    """Accept a loan offer."""
    offer = get_object_or_404(LoanOffer, id=offer_id, application__borrower=request.user)
    
    if offer.is_expired:
        messages.error(request, 'This offer has expired.')
        return redirect('loans:application_detail', pk=offer.application.id)
    
    if request.method == 'POST':
        offer.status = 'accepted'
        offer.responded_at = timezone.now()
        offer.save()
        
        # Update application
        application = offer.application
        application.status = 'offer_accepted'
        application.amount_approved = offer.amount_offered
        application.interest_rate_approved = offer.interest_rate
        application.monthly_payment = offer.monthly_payment
        application.total_repayment = offer.total_repayment
        application.save()
        
        # Decline other offers
        offer.application.offers.exclude(id=offer.id).update(status='withdrawn')
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            activity_type='offer_accepted',
            description=f'Accepted loan offer from {offer.lender.company_name or offer.lender.get_full_name()}'
        )
        
        # Create notification
        NotificationService.create_notification(
            user=offer.lender,
            notification_type='offer_accepted',
            title='Loan Offer Accepted',
            message=f'{request.user.get_full_name()} has accepted your loan offer.',
            related_object=offer
        )
        
        messages.success(request, 'You have accepted the loan offer!')
        return redirect('loans:application_detail', pk=application.id)
    
    return render(request, 'loans/accept_offer.html', {'offer': offer})


@login_required
def decline_offer(request, offer_id):
    """Decline a loan offer."""
    offer = get_object_or_404(LoanOffer, id=offer_id, application__borrower=request.user)
    
    if request.method == 'POST':
        offer.status = 'declined'
        offer.responded_at = timezone.now()
        offer.response_notes = request.POST.get('reason', '')
        offer.save()
        
        messages.info(request, 'You have declined the loan offer.')
        return redirect('loans:application_detail', pk=offer.application.id)
    
    return render(request, 'loans/decline_offer.html', {'offer': offer})


# ============== LENDER VIEWS ==============

@login_required
def lender_products(request):
    """List lender's loan products."""
    if not request.user.is_lender:
        messages.error(request, 'Only lenders can access this page.')
        return redirect('marketplace:dashboard')
    
    products = LoanProduct.objects.filter(lender=request.user)
    
    context = {
        'products': products,
    }
    return render(request, 'loans/lender_products.html', context)


@login_required
def create_product(request):
    """Create a new loan product."""
    if not request.user.is_lender:
        messages.error(request, 'Only lenders can create loan products.')
        return redirect('marketplace:dashboard')
    
    if request.method == 'POST':
        form = LoanProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.lender = request.user
            product.save()
            messages.success(request, 'Loan product created successfully!')
            return redirect('loans:lender_products')
    else:
        form = LoanProductForm()
    
    return render(request, 'loans/product_form.html', {'form': form, 'title': 'Create Loan Product'})


@login_required
def edit_product(request, pk):
    """Edit a loan product."""
    product = get_object_or_404(LoanProduct, id=pk, lender=request.user)
    
    if request.method == 'POST':
        form = LoanProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan product updated successfully!')
            return redirect('loans:lender_products')
    else:
        # Convert lists to text for form
        initial = {
            'features': '\n'.join(product.features) if product.features else '',
            'requirements': '\n'.join(product.requirements) if product.requirements else '',
        }
        form = LoanProductForm(instance=product, initial=initial)
    
    return render(request, 'loans/product_form.html', {'form': form, 'title': 'Edit Loan Product', 'product': product})


@login_required
def incoming_applications(request):
    """View incoming loan applications for lenders."""
    if not request.user.is_lender:
        messages.error(request, 'Only lenders can view incoming applications.')
        return redirect('marketplace:dashboard')
    
    # Get applications matching lender's products
    applications = LoanApplication.objects.filter(
        Q(loan_product__lender=request.user) | 
        Q(offers__lender=request.user)
    ).distinct().select_related('borrower', 'loan_product').order_by('-created_at')
    
    # Apply filters
    filter_form = ApplicationFilterForm(request.GET)
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data.get('status'):
            applications = applications.filter(status=data['status'])
        if data.get('loan_type'):
            applications = applications.filter(loan_type=data['loan_type'])
        if data.get('date_from'):
            applications = applications.filter(created_at__date__gte=data['date_from'])
        if data.get('date_to'):
            applications = applications.filter(created_at__date__lte=data['date_to'])
        if data.get('search'):
            search = data['search']
            applications = applications.filter(
                Q(borrower__first_name__icontains=search) |
                Q(borrower__last_name__icontains=search) |
                Q(id__icontains=search)
            )
    
    context = {
        'applications': applications,
        'filter_form': filter_form,
    }
    return render(request, 'loans/incoming_applications.html', context)


@login_required
def review_application(request, pk):
    """Review a loan application as a lender."""
    if not request.user.is_lender:
        messages.error(request, 'Only lenders can review applications.')
        return redirect('marketplace:dashboard')
    
    application = get_object_or_404(LoanApplication, id=pk)
    
    # Check if lender has a matching product
    matching_products = LoanProduct.objects.filter(
        lender=request.user,
        status='active'
    )
    
    # Get credit score
    credit_score = None
    try:
        credit_score = CreditScore.objects.get(user=application.borrower)
    except CreditScore.DoesNotExist:
        pass
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            amount = Decimal(request.POST.get('amount_approved', 0))
            rate = Decimal(request.POST.get('interest_rate_approved', 0))
            application.approve(request.user, amount, rate)
            
            # Create notification
            NotificationService.create_notification(
                user=application.borrower,
                notification_type='loan_approved',
                title='Loan Application Approved',
                message=f'Your loan application has been approved by {request.user.company_name or request.user.get_full_name()}.',
                related_object=application
            )
            
            messages.success(request, 'Application approved successfully!')
            
        elif action == 'reject':
            notes = request.POST.get('status_notes', '')
            application.reject(notes)
            
            NotificationService.create_notification(
                user=application.borrower,
                notification_type='loan_rejected',
                title='Loan Application Rejected',
                message=f'Your loan application was not approved. Reason: {notes}',
                related_object=application
            )
            
            messages.info(request, 'Application rejected.')
        
        return redirect('loans:incoming_applications')
    
    context = {
        'application': application,
        'credit_score': credit_score,
        'matching_products': matching_products,
    }
    return render(request, 'loans/review_application.html', context)


@login_required
def make_offer(request, application_id):
    """Make a loan offer to a borrower."""
    if not request.user.is_lender:
        messages.error(request, 'Only lenders can make offers.')
        return redirect('marketplace:dashboard')
    
    application = get_object_or_404(LoanApplication, id=application_id)
    
    if request.method == 'POST':
        form = LoanOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.application = application
            offer.lender = request.user
            
            # Get loan product
            product_id = request.POST.get('loan_product')
            if product_id:
                offer.loan_product = get_object_or_404(LoanProduct, id=product_id, lender=request.user)
            
            # Calculate totals
            principal = offer.amount_offered
            rate = offer.interest_rate / 100 / 12
            n = offer.duration_months
            if rate > 0:
                offer.monthly_payment = principal * (rate * (1 + rate)**n) / ((1 + rate)**n - 1)
            else:
                offer.monthly_payment = principal / n
            offer.total_repayment = offer.monthly_payment * n
            offer.processing_fee = principal * (offer.loan_product.processing_fee_percent / 100) if offer.loan_product else Decimal('0')
            offer.expires_at = timezone.now() + timezone.timedelta(days=7)
            offer.save()
            
            # Create notification
            NotificationService.create_notification(
                user=application.borrower,
                notification_type='new_offer',
                title='New Loan Offer',
                message=f'You have received a new loan offer from {request.user.company_name or request.user.get_full_name()}.',
                related_object=offer
            )
            
            messages.success(request, 'Loan offer sent successfully!')
            return redirect('loans:incoming_applications')
    else:
        # Pre-populate form
        initial = {
            'amount_offered': application.amount_requested,
            'duration_months': application.duration_months,
        }
        if application.loan_product:
            initial['interest_rate'] = application.loan_product.interest_rate
        form = LoanOfferForm(initial=initial)
    
    # Get lender's products
    products = LoanProduct.objects.filter(lender=request.user, status='active')
    
    context = {
        'form': form,
        'application': application,
        'products': products,
    }
    return render(request, 'loans/make_offer.html', context)


# ============== CREDIT SCORE ==============

@login_required
def credit_score_view(request):
    """View borrower's credit score."""
    if not request.user.is_borrower:
        messages.error(request, 'Only borrowers can view credit scores.')
        return redirect('marketplace:dashboard')
    
    try:
        credit_score = CreditScore.objects.get(user=request.user)
    except CreditScore.DoesNotExist:
        # Generate credit score
        from .credit_engine import CreditScoringEngine
        engine = CreditScoringEngine()
        credit_score = engine.calculate_score(request.user)
        messages.info(request, 'Your credit score has been calculated.')
    
    context = {
        'credit_score': credit_score,
    }
    return render(request, 'loans/credit_score.html', context)


# ============== AJAX ENDPOINTS ==============

def calculate_loan(request):
    """AJAX endpoint to calculate loan repayment."""
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        rate = Decimal(request.POST.get('rate', 0))
        months = int(request.POST.get('months', 0))
        
        if amount > 0 and rate > 0 and months > 0:
            monthly_rate = rate / 100 / 12
            if monthly_rate > 0:
                monthly_payment = amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
            else:
                monthly_payment = amount / months
            total_repayment = monthly_payment * months
            total_interest = total_repayment - amount
            
            return JsonResponse({
                'success': True,
                'monthly_payment': round(monthly_payment, 2),
                'total_repayment': round(total_repayment, 2),
                'total_interest': round(total_interest, 2),
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid parameters'})
